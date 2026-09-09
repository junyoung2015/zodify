// Labels stay available on hover and focus; Escape dismisses them.
document.querySelectorAll(".code-action").forEach((control) => {
  control.addEventListener("keydown", (event) => {
    if (event.key === "Escape") control.dataset.tooltipDismissed = "true";
  });
  for (const event of ["pointerleave", "focusout"]) {
    control.addEventListener(event, () => delete control.dataset.tooltipDismissed);
  }
});

// Optional enhancement; all content and navigation work without this script.
if (navigator.clipboard && window.isSecureContext) {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    const control = button.closest("[data-copy-control]");
    const tooltip = control.querySelector(".action-tooltip");
    const status = control.querySelector('[role="status"]');
    const label = button.getAttribute("aria-label");
    let reset;
    control.hidden = false;
    button.addEventListener("click", async () => {
      clearTimeout(reset);
      status.textContent = "";
      try {
        await navigator.clipboard.writeText(
          document.getElementById(`code-${button.dataset.copy}`).textContent,
        );
        button.dataset.state = "copied";
        tooltip.textContent = "Copied";
        status.textContent = `${label === "Copy command" ? "Command" : "Example"} copied to clipboard.`;
      } catch {
        button.dataset.state = "error";
        tooltip.textContent = "Select the code to copy";
        status.textContent = "Copy failed. Select the code and copy it manually.";
      }
      reset = setTimeout(() => {
        button.dataset.state = "idle";
        tooltip.textContent = label;
        status.textContent = "";
      }, button.dataset.state === "error" ? 6000 : 2000);
    });
  });
}
