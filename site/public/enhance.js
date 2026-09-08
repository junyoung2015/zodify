// Optional enhancement; all content and navigation work without this script.
if (navigator.clipboard && window.isSecureContext) {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(
          document.getElementById(`code-${button.dataset.copy}`).textContent,
        );
        button.textContent = "Copied";
      } catch {
        button.textContent = "Select the code to copy";
      }
    });
  });
}
