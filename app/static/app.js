(function () {
  const runId = window.VALIDUJ_RUN_ID;
  if (!runId) {
    return;
  }

  const eventsList = document.getElementById("events");
  const statusNode = document.getElementById("run-status");
  const stageNode = document.getElementById("run-stage");
  const stagesContainer = document.getElementById("stages");

  const renderEvent = (type, payload) => {
    if (!eventsList) return;
    const item = document.createElement("li");
    const title = document.createElement("strong");
    title.textContent = type;
    const body = document.createElement("span");
    body.textContent = ` ${JSON.stringify(payload)}`;
    item.appendChild(title);
    item.appendChild(body);
    eventsList.prepend(item);
  };

  const ensureStageCard = (payload) => {
    if (!stagesContainer || !payload.stage_index) return null;
    let card = document.getElementById(`stage-${payload.stage_index}`);
    if (card) return card;

    card = document.createElement("section");
    card.className = "stage-card";
    card.id = `stage-${payload.stage_index}`;
    card.innerHTML = `<h3>${payload.stage_index}. ${payload.stage_name || "Stage"}</h3>`;
    stagesContainer.appendChild(card);
    return card;
  };

  const stream = new EventSource(`/api/stream/runs/${runId}`);

  stream.addEventListener("stage_started", (event) => {
    const payload = JSON.parse(event.data);
    renderEvent("stage_started", payload);
    if (statusNode) statusNode.textContent = "running";
    if (stageNode) stageNode.textContent = payload.stage_name || "running";
    const card = ensureStageCard(payload);
    if (card) {
      card.innerHTML = `<h3>${payload.stage_index}. ${payload.stage_name}</h3><p><strong>Status:</strong> running</p>`;
    }
  });

  stream.addEventListener("stage_completed", (event) => {
    const payload = JSON.parse(event.data);
    renderEvent("stage_completed", payload);
    const card = ensureStageCard(payload);
    if (card) {
      card.innerHTML = `
        <h3>${payload.stage_index}. ${payload.stage_name}</h3>
        <p><strong>Status:</strong> completed</p>
        <p><strong>Provider:</strong> ${payload.provider_name} / ${payload.model_name}</p>
        <p>${payload.summary}</p>
      `;
    }
    if (stageNode) stageNode.textContent = payload.stage_name || "running";
  });

  stream.addEventListener("stage_progress", (event) => {
    const payload = JSON.parse(event.data);
    renderEvent("stage_progress", payload);
  });

  stream.addEventListener("run_completed", (event) => {
    const payload = JSON.parse(event.data);
    renderEvent("run_completed", payload);
    if (statusNode) statusNode.textContent = "completed";
    if (stageNode) stageNode.textContent = "Done";
    stream.close();
    window.setTimeout(() => window.location.reload(), 1200);
  });

  stream.addEventListener("run_failed", (event) => {
    const payload = JSON.parse(event.data);
    renderEvent("run_failed", payload);
    if (statusNode) statusNode.textContent = "failed";
    stream.close();
  });
})();
