function showPage(pageName) {
  document.querySelectorAll(".page").forEach((p) => p.classList.add("hidden"));
  document.getElementById(pageName).classList.remove("hidden");
}

async function askAI() {
  const prompt = document.getElementById("aiInput").value;

  let fd = new FormData();
  fd.append("prompt", prompt);

  const res = await fetch("/ai_chat", { method: "POST", body: fd });
  const text = await res.text();

  document.getElementById("aiResponse").textContent = text;
}

let water = 0;
function addCup() {
  water++;
  document.getElementById("waterCount").textContent = water;
}

window.askAI = askAI;
window.addCup = addCup;
