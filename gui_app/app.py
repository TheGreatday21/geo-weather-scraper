
from __future__ import annotations

import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from queue import Queue, Empty
from typing import List

import tkinter as tk
from tkinter import ttk, messagebox


# --- Import pipeline code (../src) ---
GUI_DIR = Path(__file__).resolve().parent.parent
PIPELINE_ROOT = GUI_DIR.parent  # WEATHER_SCRAPPING_TOOL/
sys.path.insert(0, str(PIPELINE_ROOT))


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


from src.scraper import WeatherScraper  # noqa: E402
from src.parser import WeatherParser  # noqa: E402
from src.storage import WeatherStorage  # noqa: E402


DEFAULT_LOCATIONS_TEXT = "\n".join(
    [
        "Kyaliwajjala, Kampala, UG",
        "Bugujju, Mukono, UG",
        "Seeta, Mukono, UG",
        "Namilyango, Mukono, UG",
        "Kyetume, Mukono, UG",
        "Nakasero, Kampala, UG"
    ]
)


@dataclass
class RunConfig:
    api_key: str
    delay_minutes: int
    iterations: int
    locations: List[str]


class QueueLogHandler(logging.Handler):
    def __init__(self, q: Queue[str]) -> None:
        super().__init__()
        self.q = q

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.q.put_nowait(msg)
        except Exception:
            # never crash logging
            pass


class WeatherGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Weather Data Pipeline")
        self.geometry("980x720")

        self._log_queue: Queue[str] = Queue()
        self._stop_event = threading.Event()
        self._worker_thread: threading.Thread | None = None

        self._build_ui()
        self._setup_logging()
        self._poll_logs()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, padding=12)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Weather Data Pipeline (GUI)", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text=f"Pipeline root: {PIPELINE_ROOT}", foreground="#555").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 0)
        )

        settings = ttk.LabelFrame(self, text="Settings", padding=12)
        settings.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        for c in range(6):
            settings.columnconfigure(c, weight=1)

        ttk.Label(settings, text="OpenWeather API key").grid(row=0, column=0, sticky="w")
        self.api_key_var = tk.StringVar(value=self._read_env_value("OPENWEATHER_API_KEY") or "")
        self.api_key_entry = ttk.Entry(settings, textvariable=self.api_key_var, show="•")
        self.api_key_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(8, 8))
        ttk.Button(settings, text="Save to .env", command=self._save_env).grid(
            row=0, column=4, sticky="ew"
        )

        ttk.Label(settings, text="Delay (minutes)").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.delay_var = tk.IntVar(value=int(self._read_env_value("SCRAPE_DELAY_MINUTES") or "3"))
        ttk.Spinbox(settings, from_=0, to=1440, textvariable=self.delay_var, width=8).grid(
            row=1, column=1, sticky="w", padx=(8, 0), pady=(10, 0)
        )

        ttk.Label(settings, text="Iterations").grid(row=1, column=2, sticky="w", pady=(10, 0))
        self.iter_var = tk.IntVar(value=int(self._read_env_value("NUM_ITERATIONS") or "10"))
        ttk.Spinbox(settings, from_=1, to=1_000_000_000, textvariable=self.iter_var, width=12).grid(
            row=1, column=3, sticky="w", padx=(8, 0), pady=(10, 0)
        )
        ttk.Label(settings, text="(Set a huge number to run “forever”)").grid(
            row=1, column=4, columnspan=2, sticky="w", pady=(10, 0)
        )

        ttk.Label(settings, text="Locations (one per line)").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        self.locations_text = tk.Text(settings, height=6, wrap="none")
        self.locations_text.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(6, 0))
        existing_locs = self._load_locations_from_env_or_default()
        self.locations_text.insert("1.0", "\n".join(existing_locs))

        controls = ttk.Frame(self, padding=(12, 0, 12, 12))
        controls.grid(row=2, column=0, sticky="new")
        controls.columnconfigure(3, weight=1)

        self.start_btn = ttk.Button(controls, text="Start", command=self._start)
        self.start_btn.grid(row=0, column=0, sticky="w")

        self.stop_btn = ttk.Button(controls, text="Stop", command=self._stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Button(controls, text="Open output folder", command=self._open_output_folder).grid(
            row=0, column=2, sticky="w", padx=(8, 0)
        )

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(controls, textvariable=self.status_var, foreground="#333").grid(
            row=0, column=3, sticky="e"
        )

        logs = ttk.LabelFrame(self, text="Logs", padding=12)
        logs.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        logs.columnconfigure(0, weight=1)
        logs.rowconfigure(0, weight=1)

        self.log_text = tk.Text(logs, height=18, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(logs, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    # ---------------- Logging ----------------
    def _setup_logging(self) -> None:
        root = logging.getLogger()
        root.setLevel(logging.INFO)

        handler = QueueLogHandler(self._log_queue)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        root.addHandler(handler)

    def _append_log(self, line: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_logs(self) -> None:
        try:
            while True:
                line = self._log_queue.get_nowait()
                self._append_log(line)
        except Empty:
            pass
        self.after(200, self._poll_logs)

    # ---------------- Env helpers ----------------
    def _env_path(self) -> Path:
        return PIPELINE_ROOT / ".env"

    def _read_env_value(self, key: str) -> str | None:
        env_path = self._env_path()
        if not env_path.exists():
            return None
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip()
        return None

    def _write_env_value(self, key: str, value: str) -> None:
        env_path = self._env_path()
        lines: list[str] = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()

        found = False
        out: list[str] = []
        for raw in lines:
            if raw.strip().startswith("#") or "=" not in raw:
                out.append(raw)
                continue
            k, _ = raw.split("=", 1)
            if k.strip() == key:
                out.append(f"{key}={value}")
                found = True
            else:
                out.append(raw)
        if not found:
            if out and out[-1].strip() != "":
                out.append("")
            out.append(f"{key}={value}")

        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    def _load_locations_from_env_or_default(self) -> List[str]:
        # Optional: allow LOCATIONS as newline-separated env value
        raw = self._read_env_value("LOCATIONS")
        if raw:
            # stored as \n escaped
            raw = raw.replace("\\n", "\n")
            locs = [x.strip() for x in raw.splitlines() if x.strip()]
            if locs:
                return locs
        return [x.strip() for x in DEFAULT_LOCATIONS_TEXT.splitlines() if x.strip()]

    def _save_env(self) -> None:
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Missing API key", "Please enter your OpenWeather API key.")
            return

        self._write_env_value("OPENWEATHER_API_KEY", api_key)
        self._write_env_value("SCRAPE_DELAY_MINUTES", str(int(self.delay_var.get())))
        self._write_env_value("NUM_ITERATIONS", str(int(self.iter_var.get())))

        locs = [x.strip() for x in self.locations_text.get("1.0", "end").splitlines() if x.strip()]
        self._write_env_value("LOCATIONS", "\\n".join(locs))

        messagebox.showinfo("Saved", f"Saved settings to {self._env_path()}")

    # ---------------- Run/Stop ----------------
    def _get_config(self) -> RunConfig:
        api_key = self.api_key_var.get().strip()
        delay_minutes = int(self.delay_var.get())
        iterations = int(self.iter_var.get())
        locations = [x.strip() for x in self.locations_text.get("1.0", "end").splitlines() if x.strip()]
        return RunConfig(api_key=api_key, delay_minutes=delay_minutes, iterations=iterations, locations=locations)

    def _start(self) -> None:
        cfg = self._get_config()
        if not cfg.api_key:
            messagebox.showerror("Missing API key", "Enter your API key (or click 'Save to .env').")
            return
        if not cfg.locations:
            messagebox.showerror("Missing locations", "Add at least one location.")
            return

        self._stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Running…")

        self._worker_thread = threading.Thread(target=self._run_pipeline, args=(cfg,), daemon=True)
        self._worker_thread.start()

    def _stop(self) -> None:
        self._stop_event.set()
        self.status_var.set("Stopping…")
        self.stop_btn.configure(state="disabled")

    def _run_pipeline(self, cfg: RunConfig) -> None:
        logger = logging.getLogger("gui")
        try:
            scraper = WeatherScraper(api_key=cfg.api_key)
            parser = WeatherParser()
            storage = WeatherStorage()

            all_weather_data = []
            locations_dicts = [{"name": x} for x in cfg.locations]
            delay_seconds = cfg.delay_minutes * 60

            for i in range(cfg.iterations):
                if self._stop_event.is_set():
                    logger.info("Stop requested. Finishing up…")
                    break

                logger.info("Reading %s of %s", i + 1, cfg.iterations)
                iteration_data = scraper.fetch_multiple_locations(locations_dicts)
                if iteration_data:
                    all_weather_data.extend(iteration_data)
                    logger.info("Collected %s records", len(iteration_data))
                else:
                    logger.warning("No data collected in this iteration")

                if i < cfg.iterations - 1 and delay_seconds > 0:
                    logger.info("Waiting %s minutes…", cfg.delay_minutes)
                    # wait in small increments so Stop responds quickly
                    for _ in range(delay_seconds):
                        if self._stop_event.is_set():
                            break
                        time.sleep(1)

            if all_weather_data and parser.validate_data(all_weather_data):
                df = parser.to_dataframe(all_weather_data)
                ok = storage.save_to_csv(df, append=True)
                if ok:
                    logger.info("Saved %s rows to %s", len(df), storage.get_filepath())
                else:
                    logger.error("Failed to save CSV")
            else:
                logger.warning("No valid data to save.")

            logger.info("Done.")
        except Exception as e:
            logger.exception("Run failed: %s", e)
        finally:
            self.after(0, self._on_finished)

    def _on_finished(self) -> None:
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_var.set("Idle")

    def _open_output_folder(self) -> None:
        data_dir = PIPELINE_ROOT / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # macOS: open folder
        try:
            os.system(f'open "{data_dir}"')
        except Exception:
            messagebox.showinfo("Folder", str(data_dir))


if __name__ == "__main__":
    # Use ttk themed widgets
    try:
        from tkinter import font  # noqa: F401
    except Exception:
        pass

    app = WeatherGUI()
    app.mainloop()

