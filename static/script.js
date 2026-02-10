let roomId = null;
let myTeam = null;
let currentCard = null;
let endTriggered = false;
let pollingStarted = false;

let swapSelection = [];

const roles = ["Captain","Vice Captain","Tank","Healer","Support","Support"];

/* ---------------- ROOM ---------------- */

async function createRoom() {
  const r = await fetch("/api/room/create",{method:"POST"});
  const d = await r.json();
  roomId = d.room_id;
  document.getElementById("roomInput").value = roomId;
  await joinRoom();
}

async function joinRoom() {
  roomId = document.getElementById("roomInput").value;
  const r = await fetch(`/api/room/join/${roomId}`,{method:"POST"});
  const d = await r.json();

  if (d.error) return alert(d.error);

  myTeam = d.team;

  if (!pollingStarted) {
    pollingStarted = true;
    poll();
  }
}

/* ---------------- POLLING ---------------- */

function poll() {
  setInterval(async()=>{
    if(!roomId || !myTeam) return;

    const r = await fetch(`/api/state/${roomId}/${myTeam}`);
    const state = await r.json();

    // JOIN STATUS
    document.getElementById("joinStatus").innerText =
      state.players_joined < 2
        ? "⏳ Waiting for opponent..."
        : "✅ Opponent joined";

    // TURN STATUS
    document.getElementById("turnStatus").innerText =
      state.your_turn ? "🟢 Your turn" : "🔴 Opponent's turn";

    renderSlots(state.your_team);

    // 🔥 ENDGAME (ONCE)
    if (!endTriggered && (state.phase === "SWAP" || state.phase === "RESULT")) {
      endTriggered = true;
      disableGameControls(true);

      if (state.phase === "SWAP") {
        showSwapUI(state.your_team);
      } else {
        showResult();
      }
    }

  },1000);
}

/* ---------------- ACTIONS ---------------- */

async function draw() {
  const r = await fetch(`/api/draw/${roomId}/${myTeam}`);
  const d = await r.json();
  if(d.error) return alert(d.error);

  currentCard = d.name;
  document.getElementById("currentCard").innerText = d.name;
}

async function assign(slot) {
  if(!currentCard) return alert("Draw a character first");

  const r = await fetch(`/api/assign/${roomId}`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({team:myTeam,slot})
  });

  const d = await r.json();
  if(d.error) return alert(d.error);

  currentCard = null;
  document.getElementById("currentCard").innerText = "";
}

async function skip() {
  const r = await fetch(`/api/skip/${roomId}/${myTeam}`,{method:"POST"});
  const d = await r.json();
  if(d.error) return alert(d.error);

  currentCard = null;
  document.getElementById("currentCard").innerText = "";
}

/* ---------------- UI ---------------- */

function renderSlots(team) {
  const div=document.getElementById("slots");
  div.innerHTML="";
  team.forEach((c,i)=>{
    div.innerHTML+=`
      <div onclick="assign(${i})">
        ${roles[i]}: ${c ? c.name : "Empty"}
      </div>`;
  });
}

function disableGameControls(disabled) {
  document.getElementById("drawBtn").disabled = disabled;
  document.getElementById("skipBtn").disabled = disabled;
}

/* ---------------- SWAP ---------------- */

function showSwapUI(team) {
  const div = document.getElementById("swapSlots");
  div.innerHTML = "";
  swapSelection = [];

  team.forEach((c, i) => {
    const el = document.createElement("div");
    el.className = "swap-slot";
    el.innerText = `${roles[i]}: ${c.name}`;
    el.onclick = () => toggleSwap(i, el);
    div.appendChild(el);
  });

  document.getElementById("swapPopup").classList.remove("hidden");
}

function toggleSwap(index, el) {
  if (swapSelection.includes(index)) {
    swapSelection = swapSelection.filter(i => i !== index);
    el.classList.remove("selected");
  } else {
    if (swapSelection.length === 2) return;
    swapSelection.push(index);
    el.classList.add("selected");
  }
}

async function confirmSwap() {
  if (swapSelection.length !== 2) {
    return alert("Select exactly two roles to swap");
  }

  const r = await fetch(`/api/swap/${roomId}`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      team: myTeam,
      from: swapSelection[0],
      to: swapSelection[1]
    })
  });

  const d = await r.json();
  if (d.error) return alert(d.error);

  document.getElementById("swapPopup").classList.add("hidden");
  showResult();
}

/* ---------------- RESULT ---------------- */

let resultShown = false;

async function showResult(){
  if(resultShown) return;
  resultShown = true;

  const r = await fetch(`/api/result/${roomId}`);
  const data = await r.json();

  const box = document.getElementById("resultContent");
  box.innerHTML = "";

  for(let i=0;i<data.rounds.length;i++){
    await new Promise(res=>setTimeout(res,700));
    const rr = data.rounds[i];
    box.innerHTML += `<p>${rr.role.toUpperCase()}: ${rr.winner}</p>`;
  }

  box.innerHTML += `<h3>🏆 ${data.final_winner}</h3>`;
  document.getElementById("resultPopup").classList.remove("hidden");
}

function closeResult(){
  document.getElementById("resultPopup").classList.add("hidden");
}