/*
  FRONT-END PROTOTYPE:
  Chat responses are simulated.
  Quiz videos must be supplied locally.
  Replace the example videos and meanings with verified dataset records.
*/

const demoSigns = {
  "عامل إيه": { english: "How are you" },
  "بحب": { english: "I love" },
  "بسرعة": { english: "Quickly" },
  "صباح الخير": { english: "Good morning" }
};

const messages = document.getElementById("messages");
const input = document.getElementById("userInput");
const chatbox = document.getElementById("chatbox");
const chatMaximize = document.getElementById("chatMaximize");

function hasArabic(text) {
  return /[\u0600-\u06FF]/.test(text);
}

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = "message " + type;
  div.dir = hasArabic(text) ? "rtl" : "ltr";
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

chatMaximize.addEventListener("click", () => {
  const maximized = chatbox.classList.toggle("maximized");
  chatMaximize.textContent = maximized ? "×" : "⛶";
  chatMaximize.setAttribute("aria-label", maximized ? "Close maximized chat" : "Maximize chat");
  chatMaximize.title = maximized ? "Close maximized chat" : "Maximize chat";
});

function showHandover(handover) {
  const existing = document.getElementById("handover-card");
  if (existing) {
    existing.scrollIntoView({ behavior: "smooth", block: "nearest" });
    return;
  }

  const card = document.createElement("div");
  card.className = "handover-card";
  card.id = "handover-card";
  card.dir = "rtl";

  const title = document.createElement("strong");
  title.textContent = "اطلب تأكيدًا من مختص";
  const message = document.createElement("span");
  message.textContent = handover.message;
  card.append(title, message);

  if (handover.url) {
    const link = document.createElement("a");
    link.href = handover.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "فتح المصدر الموثوق ↗";
    card.appendChild(link);
  }

  messages.appendChild(card);
  messages.scrollTop = messages.scrollHeight;
}

function addRecoveryActions(word, handover, retryAction) {
  const actions = document.createElement("div");
  actions.className = "message-actions";

  const addButton = (label, action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", action);
    actions.appendChild(button);
  };

  if (retryAction) {
    addButton("حاول مرة أخرى", retryAction);
  }
  addButton("جرّب كلمة أخرى", () => input.focus());
  addButton("عدّل الكلمة", () => {
    input.value = word;
    input.focus();
  });
  addButton("ابدأ من جديد", () => {
    messages.replaceChildren();
    addMessage("أهلاً بيك! اكتب كلمة أو اختَر مثالاً للبدء.", "bot-message");
    input.focus();
  });

  if (handover) {
    addButton("اسأل مختصًا", () => showHandover(handover));
  }

  messages.appendChild(actions);
  messages.scrollTop = messages.scrollHeight;
}

function addClientErrorTrace(error, word) {
  const trace = {
    trace_id: `client-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    input: word,
    rule: "R6",
    result_type: "system_error",
    error_type: error && error.name ? error.name : "NetworkError",
    detected_intent: "client_connection_failure"
  };
  try {
    const traces = JSON.parse(localStorage.getItem("ishara-client-traces") || "[]");
    traces.push(trace);
    localStorage.setItem("ishara-client-traces", JSON.stringify(traces.slice(-20)));
  } catch (storageError) {
    console.warn("Unable to persist client error trace.", storageError);
  }
  return trace;
}

function addTraceButton(traceId, container, label = "Why this result?") {
  if (!traceId) return;
  const traceButton = document.createElement("button");
  traceButton.type = "button";
  traceButton.className = "trace-toggle";
  traceButton.textContent = label;
  traceButton.addEventListener("click", () => {
    traceButton.disabled = true;
    showTrace(traceId, container);
  });
  container.appendChild(traceButton);
}

function addSuggestedExamples(examples) {
  if (!Array.isArray(examples) || examples.length === 0) return;
  const actions = document.createElement("div");
  actions.className = "message-actions";
  examples.forEach((example) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = example;
    button.addEventListener("click", () => sendWord(example));
    actions.appendChild(button);
  });
  messages.appendChild(actions);
  messages.scrollTop = messages.scrollHeight;
}

function showRelatedResults(data, searchedWord) {
  const message = document.createElement("div");
  message.className = "message bot-message";
  message.dir = "rtl";
  const intro = document.createElement("p");
  intro.textContent = data.reply;
  message.appendChild(intro);

  (data.related || []).slice(0, 3).forEach((entry) => {
    const item = document.createElement("div");
    item.className = "result-card";
    const badge = document.createElement("p");
    badge.className = "result-label";
    badge.textContent = entry.badge || "Related, not the same word";
    const label = document.createElement("p");
    label.style.fontWeight = "800";
    label.textContent = `${entry.arabic} · ${entry.english}`;
    const reason = document.createElement("p");
    reason.textContent = `${entry.reason} · Similarity: ${Math.round(entry.score * 100)}%`;
    item.append(badge, label, reason);
    message.appendChild(item);
  });

  addTraceButton(data.trace_id, message, "Why these suggestions?");
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
  addRecoveryActions(searchedWord, data.handover);
}

async function showTrace(traceId, container) {
  try {
    let trace;
    try {
      const response = await fetch(`http://127.0.0.1:8000/trace/${traceId}`);
      if (!response.ok) throw new Error("Trace unavailable");
      trace = await response.json();
    } catch (serverError) {
      const localTraces = JSON.parse(localStorage.getItem("ishara-client-traces") || "[]");
      trace = localTraces.find((item) => item.trace_id === traceId);
      if (!trace) throw serverError;
    }
    const panel = document.createElement("div");
    panel.className = "trace-panel";
    const details = [
      `Rule: ${trace.rule || "unknown"}`,
      `Result: ${trace.result_type || "unknown"}`
    ];
    if (trace.matched_field) details.push(`Field: ${trace.matched_field}`);
    if (trace.matched_alias) details.push(`Alias: ${trace.matched_alias}`);
    if (trace.matched_entry) details.push(`Entry: ${trace.matched_entry}`);
    if (trace.best_candidate) details.push(`Best candidate: ${trace.best_candidate.id} (${trace.best_score})`);
    if (trace.threshold !== undefined && trace.threshold !== null) details.push(`Threshold: ${trace.threshold}`);
    if (trace.error_type) details.push(`Error: ${trace.error_type}`);
    if (trace.detected_intent) details.push(`Intent: ${trace.detected_intent}`);
    if (trace.scores) details.push(`Scores: ${trace.scores.map((item) => `${item.entry_id} ${item.score}`).join(", ")}`);
    if (trace.entries) details.push(`Relation notes: ${trace.entries.map((item) => `${item.entry_id}: ${item.relation_note || "related but not the same word"}`).join("; ")}`);
    if (trace.system_issue) details.push(`System issue: ${trace.system_issue.rule} · ${trace.system_issue.error_type}`);
    panel.textContent = details.join(" · ");
    container.appendChild(panel);
  } catch (error) {
    addMessage("The explanation is unavailable right now. Please try again.", "bot-message");
  }
}

function addVideoExpandButton(video, container) {
  const replayButton = document.createElement("button");
  replayButton.type = "button";
  replayButton.className = "video-replay";
  replayButton.textContent = "إعادة ↺";
  replayButton.setAttribute("aria-label", "Replay sign video");
  replayButton.addEventListener("click", () => {
    video.currentTime = 0;
    video.play().catch(() => {});
  });

  const speedButton = document.createElement("button");
  const playbackRates = [1, 0.75, 0.5];
  let playbackRateIndex = 0;
  speedButton.type = "button";
  speedButton.className = "video-speed";
  speedButton.textContent = "1×";
  speedButton.setAttribute("aria-label", "Change playback speed");
  speedButton.addEventListener("click", () => {
    playbackRateIndex = (playbackRateIndex + 1) % playbackRates.length;
    video.playbackRate = playbackRates[playbackRateIndex];
    speedButton.textContent = `${playbackRates[playbackRateIndex]}×`;
  });

  const expandButton = document.createElement("button");
  expandButton.type = "button";
  expandButton.className = "video-expand";
  expandButton.textContent = "تكبير ⛶";
  expandButton.setAttribute("aria-label", "Open video fullscreen");
  expandButton.addEventListener("click", () => {
    if (container.requestFullscreen) {
      container.requestFullscreen();
    } else if (video.webkitEnterFullscreen) {
      video.webkitEnterFullscreen();
    }
  });

  container.append(replayButton, speedButton, expandButton);
}

function sendWord(word) {
  input.value = word;
  document.getElementById("chatForm").requestSubmit();
}

document.getElementById("chatForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const word = input.value.trim();
    if (!word) return;

    addMessage(word, "user-message");
    input.value = "";
    let requestTimeout;
    const retryCurrentWord = () => {
        input.value = word;
        document.getElementById("chatForm").requestSubmit();
    };

    try {
        const controller = new AbortController();
        requestTimeout = setTimeout(() => controller.abort(), 15000);
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: word
            }),
            signal: controller.signal
        });
        clearTimeout(requestTimeout);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            if (data.rule === "R6") {
                const errorMessage = addMessage(data.reply || "واجهنا مشكلة مؤقتة. حاول مرة أخرى بعد قليل.", "bot-message");
                addTraceButton(data.trace_id, errorMessage, "Why this error?");
                addRecoveryActions(word, null, retryCurrentWord);
                return;
            }
            if (data.rule === "R5") {
                const scopeMessage = addMessage(data.reply, "bot-message");
                addTraceButton(data.trace_id, scopeMessage, "Why this input was rejected?");
                addRecoveryActions(word, null);
                return;
            }
            const apiError = new Error(data.detail || "Backend request failed");
            apiError.name = data.error_type || "APIError";
            throw apiError;
        }

        if (data.status === "quiz") {
            addMessage(data.reply, "bot-message");
            document.querySelector("#quiz").scrollIntoView({ behavior: "smooth" });
            loadQuiz();
            return;
        }

        if (data.status === "related") {
            showRelatedResults(data, word);
            return;
        }

        // If no matching sign was found
        if (data.status === "not_found" || data.status === "out_of_scope") {
            if (data.model_reply) {
                addMessage(data.model_reply, "bot-message");
            }
            addMessage(data.reply, "bot-message");
            addRecoveryActions(word, data.handover);
            if (data.status === "not_found") {
                addSuggestedExamples(data.suggested_examples);
            }
            return;
        }

        // Create the bot message
        const div = document.createElement("div");
        div.className = "message bot-message";

        // Display the reply
        const intro = document.createElement("div");
        intro.textContent = data.reply;
        div.appendChild(intro);

        if (data.model_reply) {
            const modelReply = document.createElement("p");
            modelReply.textContent = data.model_reply;
            div.appendChild(modelReply);
        }

        // Create result card
        const card = document.createElement("div");
        card.className = "result-card";

        // Create the actual video element
        const video = document.createElement("video");
        video.controls = true;
        video.preload = "metadata";
        video.playsInline = true;
        video.src = "http://127.0.0.1:8000" + data.video_url;

        const videoFrame = document.createElement("div");
        videoFrame.className = "video-frame";
        videoFrame.appendChild(video);
        addVideoExpandButton(video, videoFrame);
        card.appendChild(videoFrame);

        // Display word translations
        const title = document.createElement("p");
        title.style.fontWeight = "800";
        title.dir = "rtl";
        title.textContent = data.arabic + " · " + data.english;
        card.appendChild(title);

        const label = document.createElement("p");
        label.className = "result-label";
        label.textContent = data.result_label;
        card.appendChild(label);

        addTraceButton(data.trace_id, card);

        div.appendChild(card);

        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;

        if (data.system_issue) {
            const warning = addMessage(data.system_warning, "bot-message");
            addTraceButton(data.trace_id, warning, "Why this error?");
            addRecoveryActions(word, null, retryCurrentWord);
        }

    } catch (error) {
        clearTimeout(requestTimeout);
        console.error("Chat error:", error);
        const trace = addClientErrorTrace(error, word);
        const errorMessage = addMessage(
            `تعذر الاتصال بالخدمة الآن. حاول مرة أخرى. رقم التتبع: ${trace.trace_id}`,
            "bot-message"
        );
        addTraceButton(trace.trace_id, errorMessage, "Why this error?");
        addRecoveryActions(word, null, retryCurrentWord);
    }
});

/* QUIZ: video + four meaning choices */


/* QUIZ: Load questions from Ishara Backend */

let questions = [];
let current = 0;
let score = 0;
let answered = false;

function updateScoreProgress() {
  const total = questions.length;
  const progressBar = document.getElementById("progressBar");
  const percentage = total ? (score / total) * 100 : 0;

  document.getElementById("scorePill").textContent =
    `Score: ${score} / ${total}`;
  progressBar.style.width = `${percentage}%`;
  progressBar.classList.toggle("complete", total > 0 && score === total);
  document.getElementById("progressLabel").textContent =
    `Score progress: ${score} of ${total}`;
}

async function loadQuiz() {
  const content = document.getElementById("quizContent");

  try {
    content.textContent = "Loading quiz questions...";

    const response = await fetch("http://127.0.0.1:8000/quiz");

    if (!response.ok) {
      throw new Error("Failed to load quiz questions");
    }

    const data = await response.json();

    if (data.status !== "success" || !data.questions.length) {
      throw new Error("No quiz questions available");
    }

    const allWords = data.questions;

    questions = allWords.map(question => {
      const otherWords = allWords.filter(
        word => word.id !== question.id
      );

      const wrongOptions = otherWords
        .map(word => word.arabic)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);

      const options = [
        question.arabic,
        ...wrongOptions
      ].sort(() => Math.random() - 0.5);

      return {
        word: question.arabic,
        video: "http://127.0.0.1:8000" + question.video_url,
        options: options,
        correct: options.indexOf(question.arabic)
      };
    });

    current = 0;
    score = 0;
    updateScoreProgress();
    renderQuestion();

  } catch (error) {
    console.error("Quiz loading error:", error);
    content.textContent =
      "Unable to load the quiz. Please check your connection.";
  }
}

function renderQuestion() {
  answered = false;

  const q = questions[current];
  const content = document.getElementById("quizContent");
  const nextBtn = document.getElementById("nextBtn");

  content.replaceChildren();
  nextBtn.disabled = true;
  nextBtn.style.display = "inline-block";
  nextBtn.textContent =
    current === questions.length - 1 ? "See results →" : "Next question →";

  document.getElementById("quizStatus").textContent =
    `Question ${current + 1} of ${questions.length}`;
  updateScoreProgress();

  const count = document.createElement("div");
  count.className = "question-count";
  count.textContent = `QUESTION 0${current + 1}`;
  content.appendChild(count);

  const videoBox = document.createElement("div");
  videoBox.className = "quiz-video-box";

  const video = document.createElement("video");
  video.className = "quiz-video";
  video.controls = true;
  video.preload = "metadata";
  video.playsInline = true;
  video.src = q.video;

  const videoFrame = document.createElement("div");
  videoFrame.className = "video-frame";
  videoFrame.appendChild(video);
  addVideoExpandButton(video, videoFrame);
  videoBox.appendChild(videoFrame);

  const label = document.createElement("div");
  label.className = "quiz-video-label";
  label.textContent = "Watch carefully, then choose the meaning.";
  videoBox.appendChild(label);

  content.appendChild(videoBox);

  const title = document.createElement("div");
  title.className = "question";
  title.textContent = "What does this sign mean?";
  content.appendChild(title);

  const answers = document.createElement("div");
  answers.className = "answers";

  q.options.forEach((option, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "answer";

    const letter = document.createElement("span");
    letter.className = "answer-letter";
    letter.textContent = String.fromCharCode(65 + index);

    const text = document.createElement("span");
    text.textContent = option;

    button.append(letter, text);
    button.addEventListener("click", () => chooseAnswer(index));
    answers.appendChild(button);
  });

  content.appendChild(answers);

  const feedback = document.createElement("div");
  feedback.className = "feedback";
  feedback.id = "feedback";
  content.appendChild(feedback);
}

function chooseAnswer(index) {
  if (answered) return;
  answered = true;

  const q = questions[current];
  const buttons = document.querySelectorAll("#quizContent .answer");
  const feedback = document.getElementById("feedback");

  buttons.forEach(button => button.disabled = true);
  buttons[q.correct].classList.add("correct");

  if (index === q.correct) {
    score++;
    feedback.textContent = "✓ Correct! Great job!";
    feedback.style.color = "#237544";
  } else {
    buttons[index].classList.add("wrong");
    feedback.textContent =
      `Not quite! The correct answer is "${q.options[q.correct]}".`;
    feedback.style.color = "#b44c3e";
  }

  updateScoreProgress();

  document.getElementById("nextBtn").disabled = false;
}

function nextQuestion() {
  if (!answered) return;

  if (current < questions.length - 1) {
    current++;
    renderQuestion();
  } else {
    showResults();
  }
}

function showResults() {
  const content = document.getElementById("quizContent");
  content.replaceChildren();

  updateScoreProgress();
  document.getElementById("quizStatus").textContent = "Quiz completed!";

  const heading = document.createElement("h3");
  heading.textContent = score === questions.length
    ? "🏆 Perfect score!"
    : "🌟 Quiz completed!";
  content.appendChild(heading);

  const result = document.createElement("p");
  result.textContent =
    `You scored ${score} out of ${questions.length}. Keep practicing!`;
  content.appendChild(result);

  const restart = document.createElement("button");
  restart.className = "btn btn-primary";
  restart.textContent = "↻ Try again";
  restart.onclick = () => {
    loadQuiz();
  };
  content.appendChild(restart);

  document.getElementById("nextBtn").style.display = "none";
}

loadQuiz();
