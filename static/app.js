const stage = document.querySelector("#stage");
const countLabel = document.querySelector("#scene-count");
const refreshButton = document.querySelector("#refresh-scene");
const template = document.querySelector("#pigeon-template");
const backgroundMusic = document.querySelector("#background-music");
const jokeSound = document.querySelector("#joke-sound");
const kissSound = document.querySelector("#kiss-sound");

let activeKissTimer;
let currentVersion;
let musicStarted = false;

if (jokeSound) jokeSound.volume = 0.95;
if (kissSound) kissSound.volume = 1;

function assetFor(kind) {
  return "/static/assets/pigeon-cutout.png";
}

function startBackgroundMusic() {
  if (!backgroundMusic || musicStarted) return;

  backgroundMusic.volume = 0.16;
  backgroundMusic.playbackRate = 1;
  backgroundMusic
    .play()
    .then(() => {
      musicStarted = true;
    })
    .catch(() => {
      musicStarted = false;
    });
}

function playLocalSound(sound) {
  if (!sound) return;

  const effect = new Audio(sound.currentSrc || sound.src);
  effect.volume = sound.volume;
  effect.play().catch(() => {});
}

function tellJoke(pigeon) {
  if (pigeon.classList.contains("talking")) {
    pigeon.classList.remove("talking");
    return;
  }

  const bubble = pigeon.querySelector(".bubble");
  bubble.textContent = pigeon.dataset.joke || "Coo. The joke flew away.";
  pigeon.classList.add("talking");
  playLocalSound(jokeSound);
}

function setKissMotion(left, right) {
  const leftBox = left.getBoundingClientRect();
  const rightBox = right.getBoundingClientRect();

  const leftCenter = {
    x: leftBox.left + leftBox.width / 2,
    y: leftBox.top + leftBox.height / 2,
  };
  const rightCenter = {
    x: rightBox.left + rightBox.width / 2,
    y: rightBox.top + rightBox.height / 2,
  };
  const midpoint = {
    x: (leftCenter.x + rightCenter.x) / 2,
    y: (leftCenter.y + rightCenter.y) / 2,
  };
  const finalGap = Math.min(leftBox.width, rightBox.width) * 0.36;
  const leftTarget = { x: midpoint.x - finalGap, y: midpoint.y };
  const rightTarget = { x: midpoint.x + finalGap, y: midpoint.y };

  left.style.setProperty("--kiss-x", `${leftTarget.x - leftCenter.x}px`);
  left.style.setProperty("--kiss-y", `${leftTarget.y - leftCenter.y}px`);
  right.style.setProperty("--kiss-x", `${rightTarget.x - rightCenter.x}px`);
  right.style.setProperty("--kiss-y", `${rightTarget.y - rightCenter.y}px`);

  let heart = stage.querySelector(".kiss-heart");
  if (!heart) {
    heart = document.createElement("span");
    heart.className = "kiss-heart";
    heart.setAttribute("aria-hidden", "true");
    heart.textContent = "♥";
    stage.appendChild(heart);
  }

  const stageBox = stage.getBoundingClientRect();
  heart.style.left = `${midpoint.x - stageBox.left}px`;
  heart.style.top = `${midpoint.y - stageBox.top - Math.min(leftBox.width, rightBox.width) * 0.46}px`;
  heart.classList.remove("show");
  void heart.offsetWidth;
  heart.classList.add("show");
}

function handlePigeonClick(pigeon) {
  if (pigeon.dataset.behavior !== "kiss") {
    tellJoke(pigeon);
    return;
  }

  const pair = document.querySelectorAll('.pigeon[data-behavior="kiss"]');
  const left = document.querySelector('.pigeon[data-pair-role="left"]');
  const right = document.querySelector('.pigeon[data-pair-role="right"]');
  if (!left || !right) return;

  pair.forEach((node) => {
    node.classList.remove("kissing-now");
  });
  setKissMotion(left, right);
  void stage.offsetWidth;
  pair.forEach((node) => {
    node.classList.add("kissing-now");
  });

  playLocalSound(kissSound);
  clearTimeout(activeKissTimer);
  activeKissTimer = setTimeout(() => {
    pair.forEach((node) => {
      node.classList.remove("kissing-now");
    });
    stage.querySelector(".kiss-heart")?.classList.remove("show");
  }, 1800);
}

function clearPigeons() {
  stage.querySelectorAll(".pigeon").forEach((node) => node.remove());
}

stage.addEventListener("click", (event) => {
  startBackgroundMusic();
  const pigeon = event.target.closest(".pigeon");
  if (!pigeon || !stage.contains(pigeon)) return;
  handlePigeonClick(pigeon);
});

window.addEventListener("pointerdown", startBackgroundMusic, { once: true });
window.addEventListener("keydown", startBackgroundMusic, { once: true });

function renderPigeon(pigeon) {
  const node = template.content.firstElementChild.cloneNode(true);
  const image = node.querySelector(".pigeon-image");

  node.id = pigeon.id;
  node.dataset.behavior = pigeon.behavior;
  node.dataset.facing = pigeon.facing;
  node.dataset.joker = String(pigeon.isJoker);
  node.dataset.joke = pigeon.joke || "";
  node.dataset.pairRole = pigeon.pairRole || "";
  node.style.left = `${pigeon.x}%`;
  node.style.top = `${pigeon.y}%`;
  node.style.setProperty("--delay", `${pigeon.delay}s`);
  node.style.setProperty("--scale", pigeon.scale);
  node.setAttribute("aria-label", "Pigeon");

  image.src = assetFor("regular");
  image.alt = "Pigeon";
  stage.appendChild(node);
}

async function loadScene() {
  if (countLabel) countLabel.textContent = "Gathering pigeons...";
  if (refreshButton) refreshButton.disabled = true;
  clearPigeons();

  const response = await fetch("/api/pigeons", { cache: "no-store" });
  if (!response.ok) throw new Error("Could not load pigeons");
  const scene = await response.json();

  scene.pigeons.forEach(renderPigeon);
  if (countLabel) {
    countLabel.textContent = `${scene.count} pigeons. Every single pigeon tells jokes except the kissing pair.`;
  }
  if (refreshButton) refreshButton.disabled = false;
}

if (refreshButton) {
  refreshButton.addEventListener("click", () => {
    loadScene().catch(() => {
      if (countLabel) countLabel.textContent = "The flock failed to arrive.";
      refreshButton.disabled = false;
    });
  });
}

loadScene().catch(() => {
  if (countLabel) countLabel.textContent = "The flock failed to arrive.";
  if (refreshButton) refreshButton.disabled = false;
});

async function pollVersion() {
  try {
    const response = await fetch("/api/version", { cache: "no-store" });
    if (!response.ok) return;

    const { version } = await response.json();
    if (!currentVersion) {
      currentVersion = version;
      return;
    }

    if (version !== currentVersion) {
      window.location.reload();
    }
  } catch {
    // During container hot reload the server can be unavailable briefly.
  }
}

setInterval(pollVersion, 1000);
pollVersion();
