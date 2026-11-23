
/* ---------------------------------------------------------------
   CoMind / Ishara frontend. All answers come from the FastAPI backend.
   The "Why this result?" panel is drawn only from the decision trace.
   The website is Egyptian Arabic first, with an English switch.
---------------------------------------------------------------- */
const API = (location.port === "8000") ? "" : "http://127.0.0.1:8000";

/* ---------- texts ---------- */
const T = {
ar: {
  skip: "انتقل للشات", navLabel: "القائمة الرئيسية", navLearn: "اتعلم", navQuiz: "اختبار", navHelp: "مساعدة", navTry: "جرّب ↖",
  langBtn: "English",
  heroEyebrow: "✳ لغة الإشارة أقرب لك", heroTitle: "كل إشارة <em>بتقرّبنا.</em>",
  heroText: "اتعلم لغة الإشارة المصرية بفيديوهات إحنا متأكدين منها، وكلام بسيط، وتمارين خفيفة. كلمة كلمة.",
  heroStart: "ابدأ اتعلم ↖", heroQuiz: "جرّب الاختبار ✳",
  float1: "✋ اتعلم بعينك", float1s: "شوف الإشارة بتتعمل إزاي", float2: "✳ على راحتك", float2s: "من غير أي ضغط",
  learnEyebrow: "مساحة التعلم بتاعتك", learnTitle: "يلا نتعلم إشارة.",
  learnText: "اكتب كلمة بالعربي أو بالإنجليزي. كل إجابة بتقولك: الكلمة موجودة بالظبط، ولا قريبة منها، ولا مش موجودة، وتقدر تعرف ليه.",
  aboutTitle: "كلمات صغيرة.<br>تواصل أكبر.",
  aboutText: "«إشارة» مساعد ذكاء اصطناعي. بيعرض بس إشارات 56 كلمة إحنا متأكدين منها. لو مش متأكد، بيقولك بصراحة ومش بيخمّن.",
  setTitle: "الإعدادات بتاعتك", setExact: "الكلمة بالظبط بس", setExactS: "خبّي الكلمات القريبة",
  setSize: "حجم الكلام", size1: "حجم عادي", size2: "حجم كبير", size3: "حجم كبير جدًا", setContrast: "ألوان واضحة جدًا",
  browseBtn: "شوف الـ56 كلمة", helpBtn: "مساعدة ومعلومات",
  botName: "مساعد إشارة", convLabel: "المحادثة", suggLabel: "اقتراحات",
  inputLabel: "اكتب كلمة بالعربي أو بالإنجليزي", inputPh: "اكتب كلمة… / Type a word…", send: "ابعت ↖",
  hint: "اختصار: دوس <kbd>/</kbd> علشان تروح لمربع الكتابة. «مساعدة» موجودة دايمًا فوق.",
  f1t: "اتعلم بعينك", f1p: "اتفرج على كل إشارة، عيدها، وبطّأها علشان تشوف الإيد كويس.",
  f2t: "افهم النتيجة", f2p: "«ليه النتيجة دي؟» بيشرحلك بكلام بسيط إزاي وصلنا للإجابة.",
  f3t: "مفيش إشارات متألفة", f3p: "لو معندناش إشارة متأكدين منها، بنقولك. والكلمات القريبة دايمًا مكتوب عليها إنها مش نفس الكلمة.",
  quizEyebrow: "اتفرج · فكّر · جاوب", quizTitle: "تقدر تقرا الإشارة؟", quizText: "اتفرج على فيديو الإشارة واختار الكلمة اللي بتعنيها.",
  quizBox: "✋ تحدي الإشارة", quizProgress: "تقدمك في الاختبار",
  footTag: "بنتعلم نتواصل، إشارة ورا إشارة.", footData: "نموذج أولي لمشروع طلابي · الداتا: Egyptian Sign Language Recognition (Kaggle)", footBack: "ارجع للشات ↑",
  browseTitle: "الـ56 كلمة", browseText: "دي الكلمات الوحيدة اللي «إشارة» يقدر يعرضها. اختار كلمة وشوف إشارتها.", close: "اقفل",
  helpTitle: "مساعدة ومعلومات",
  conn: n => `مساعد ذكاء اصطناعي · متصل · ${n} كلمة`, connModelOn: " · النموذج شغال", connModelOff: " · ردود جاهزة",
  connFail: "مساعد ذكاء اصطناعي · مش متصل بالسيرفر",
  stage1: "البداية · خطوة 1 من 3: اتفرج", stage2: "البداية · خطوة 2 من 3: جرّب", stage3: "لوحدك دلوقتي · المساعدة فوق",
  chips1: "ابدأ من هنا:", chipExample: "▶ وريني مثال", chips2: "دورك! دوس على كلمة أو اكتب كلمتك:", chips3: "اقتراحات:",
  chipBrowse: "شوف كل الكلمات", chipQuiz: "افتح الاختبار",
  words1: ["صباح الخير", "دكتور"], words2: ["عامل إيه", "صاحب", "شكراً", "عايز"], words3: ["كتاب", "الجمعة"],
  greet: ["أهلاً بيك! 👋 أنا «إشارة»، مساعد ذكاء اصطناعي هيساعدك تتعلم لغة الإشارة المصرية."],
  can: "أقدر: أوريك فيديو الإشارة لأي كلمة من 56 كلمة، بالعربي أو بالإنجليزي، وأختبرك فيها.",
  cant: "مقدرش: أترجم محادثة، ولا أألّف إشارة من عندي، ولا أكون بديل عن مدرس لغة إشارة.",
  why: "كل إجابة عليها علامة، ولو دوست «ليه النتيجة دي؟» هقولك وصلت لها إزاي.",
  exampleStatus: "مثال: «إشارة» هيدوّر على «صباح الخير» لوحده علشان تشوف النتيجة شكلها إيه.",
  exampleAfter: "دي «مطابقة تامة»: العلامة مكتوب عليها ✓ مطابقة تامة، وتحتها الكلمة، ولو دوست «ليه النتيجة دي؟» هتعرف لقيناها إزاي. يلا دورك!",
  stage3Msg: "برافو عليك! 👏 من هنا انت لوحدك، الاقتراحات هتقل، و«مساعدة» موجودة دايمًا فوق.",
  searching: "بدوّر في الداتا…", notMeant: "دي مش الكلمة اللي أقصدها", lookingOther: "بدوّر على كلمات تانية…",
  exactOn: "اتغير الإعداد: الكلمة بالظبط بس. مش هعرض كلمات قريبة.", exactOff: "اتغير الإعداد: هعرض الكلمات القريبة، وهيبقى مكتوب عليها دايمًا.",
  netErr: "معلش، مقدرتش أوصل للسيرفر. جرب تاني.",
  badge: { R0: "معلومة", R1: "مطابقة تامة", R2: "مطابقة تامة (كلمة بنفس المعنى)", R3: "كلمة قريبة، مش نفس الكلمة", R4: "ملقيناش إشارة متأكدين منها", R5: "مش من اللي بعمله", R6: "مشكلة عندنا", R7: "محتاج حد متخصص" },
  whyBtn: "ليه النتيجة دي؟", browseAct: "شوف الـ56 كلمة", quizAct: "افتح الاختبار", retry: "جرب تاني", edit: "عدّل الكلمة", over: "ابدأ من الأول",
  slow: "بطيء 0.5×", normal: "عادي 1×", replay: "↻ عيد", speedLabel: "سرعة الفيديو",
  videoLabel: (en, ar) => `فيديو إشارة: ${ar} (${en})`,
  helpful: "مفيد", notHelpful: "مش مفيد", fbQ: "إيه اللي مكانش مظبوط؟",
  reasons: ["الإشارة غلط", "الكلمة غلط", "مش شايف كويس", "الشرح مش واضح", "حاجة تانية"], fbSend: "ابعت رأيك",
  fbOk: "✓ شكرًا! فريقنا بيراجع الآراء كل أسبوع.", fbFail: "معلش، رأيك ماتبعتش. جرب تاني.", altFail: "معلش، مقدرتش أجيب كلمات تانية. دوّر تاني.",
  needPerson: "محتاج حد متخصص؟", needPersonText: "اسأل مدرس أو مترجم لغة إشارة مصرية، أو جمعية للصم قريبة منك.",
  urgent: "مساعدة فورًا", urgentText: "الإسعاف 123 · الشرطة 122 (مصر)",
  browseFail: "مقدرتش أجيب قائمة الكلمات. اتأكد إن السيرفر شغال.",
  /* why panel */
  whyTitle: "ليه النتيجة دي؟", inShort: "باختصار:", expert: "تفاصيل للمتخصصين",
  fullTrace: "السجل الكامل (Decision trace)", allChecks: "كل الخطوات بالترتيب", considered: "الكلمات اللي قارنّا بيها",
  colEntry: "الكلمة", colScore: "التشابه", colDecision: "القرار",
  whoModel: m => `مين كتب الرد؟ نموذج الذكاء الاصطناعي (${m}) صاغ الجملة بس، واتراجعت إنها مطابقة للي حصل فعلاً. الفيديو والنتيجة اختارهم الكود مش النموذج.`,
  whoTemplate: "مين كتب الرد؟ جملة جاهزة كتبها فريقنا. الفيديو والنتيجة اختارهم الكود حسب القواعد.",
  rows: { typed: "كتبت", cleaned: "بعد التنظيف", steps: "التنظيف", looked: "الكلمة اللي دورنا عليها", rule: "القاعدة", entry: "الكلمة في الداتا", matched: "اتطابقت مع", video: "ملف الفيديو", closest: "أقرب كلمة", thr: "الحد الأدنى للتشابه", setting: "الإعداد", safety: "فحص الأمان", dataset: "الداتا", trace: "رقم السجل" },
  settingOn: "الكلمة بالظبط بس: شغال", settingOff: "الكلمة بالظبط بس: مقفول",
  pct: x => `${Math.round(x * 100)}%`,
  /* quiz */
  score: (s, n) => `النتيجة: ${s} / ${n}`, qOf: (c, n) => `سؤال ${c} من ${n}`, qNum: c => `سؤال ${c}`,
  next: "السؤال اللي بعده ←", results: "شوف النتيجة ←", watch: "اتفرج كويس، وبعدين اختار المعنى.", qText: "الإشارة دي معناها إيه؟",
  correctMark: "✓ الإجابة الصح", yourMark: "✗ إجابتك", correct: "✓ صح! برافو عليك!",
  wrong: (ar) => `✗ قربت! الإجابة الصح هي «${ar}».`, quizWhy: (id) => `ليه؟ الفيديو ده هو كلمة «${id}» في الداتا، والاختيارات التانية كلمات تانية من نفس الداتا.`,
  loading: "بجهّز الأسئلة…", quizFail: "مقدرتش أجيب الاختبار. اتأكد إن السيرفر شغال.", tryAgain: "جرب تاني",
  done: "خلصت الاختبار! 🌟", perfect: "🏆 الدرجة النهائية!", scored: (s, n) => `جبت ${s} من ${n}. كمّل تمرين!`, newQuiz: "↻ اختبار جديد", finished: "خلص الاختبار!",
  quizVideo: c => `فيديو السؤال ${c}`
},
en: {
  skip: "Skip to the chat", navLabel: "Main", navLearn: "Learn", navQuiz: "Quiz", navHelp: "Help", navTry: "Try it ↗",
  langBtn: "عربي",
  heroEyebrow: "✳ SIGN LANGUAGE, MADE CLOSER", heroTitle: "Every sign brings us <em>closer.</em>",
  heroText: "Discover Egyptian Sign Language through verified sign videos, simple words, and light practice. One word at a time.",
  heroStart: "Start learning ↗", heroQuiz: "Take the quiz ✳",
  float1: "✋ Visual learning", float1s: "See signs in action", float2: "✳ Learn at your pace", float2s: "Practice without pressure",
  learnEyebrow: "YOUR LEARNING SPACE", learnTitle: "Let's learn a sign.",
  learnText: "Type a word in Arabic or English. Every answer tells you if it is an exact match, a close word, or not found, and you can see why.",
  aboutTitle: "Small words.<br>Big connections.",
  aboutText: "Ishara is an AI assistant. It only shows signs for 56 words that we are sure of. If it isn't sure, it tells you and doesn't guess.",
  setTitle: "Your settings", setExact: "Exact matches only", setExactS: "Hide close words",
  setSize: "Text size", size1: "Normal text", size2: "Large text", size3: "Extra large text", setContrast: "High contrast",
  browseBtn: "Browse the 56 words", helpBtn: "Help and data",
  botName: "Ishara Assistant", convLabel: "Conversation", suggLabel: "Suggestions",
  inputLabel: "Type a word in Arabic or English", inputPh: "Type a word… / اكتب كلمة…", send: "Send ↗",
  hint: "Shortcut: press <kbd>/</kbd> to jump to the search box. Help is always in the top menu.",
  f1t: "Learn visually", f1p: "Watch each sign, replay it, and slow it down to see the hands clearly.",
  f2t: "Understand the result", f2p: "“Why this result?” tells you in simple words how we found each answer.",
  f3t: "No made-up signs", f3p: "If we don't have a sign we're sure of, we say so. Close words are always marked as not the same word.",
  quizEyebrow: "WATCH · THINK · ANSWER", quizTitle: "Can you read the sign?", quizText: "Watch the sign video and choose the word it means.",
  quizBox: "✋ Sign Challenge", quizProgress: "Quiz progress",
  footTag: "Learning to communicate, one sign at a time.", footData: "A student prototype · Data: Egyptian Sign Language Recognition (Kaggle)", footBack: "Back to the chat ↑",
  browseTitle: "All 56 words", browseText: "These are the only words Ishara can show. Choose one to see its sign.", close: "Close",
  helpTitle: "Help and data",
  conn: n => `AI assistant · connected · ${n} words`, connModelOn: " · model on", connModelOff: " · ready-written replies",
  connFail: "AI assistant · not connected to the server",
  stage1: "Getting started · Step 1 of 3: Watch", stage2: "Getting started · Step 2 of 3: Try it", stage3: "On your own · Help is at the top",
  chips1: "Start here:", chipExample: "▶ Show me an example", chips2: "Your turn! Tap a word or type your own:", chips3: "Suggestions:",
  chipBrowse: "Browse all words", chipQuiz: "Open the quiz",
  words1: ["Good morning", "Doctor"], words2: ["How are you", "brother", "thank you", "I want"], words3: ["Book", "Friday"],
  greet: ["Hi! 👋 I'm Ishara, an AI assistant that helps you learn Egyptian Sign Language."],
  can: "I can: show you the sign video for any of 56 words, in Arabic or English, and quiz you.",
  cant: "I can't: interpret a conversation, make up a sign, or replace a sign language teacher.",
  why: "Every answer has a label, and “Why this result?” tells you how I got it.",
  exampleStatus: "Example: Ishara searches “Good morning” by itself so you can see what a result looks like.",
  exampleAfter: "This is an exact match: the label says ✓ Exact match, the word is under it, and “Why this result?” tells you how we found it. Your turn!",
  stage3Msg: "Well done! 👏 From now on you're on your own. Suggestions fade, and Help is always at the top.",
  searching: "Searching the dataset…", notMeant: "This isn't what I meant", lookingOther: "Looking for other words…",
  exactOn: "Setting changed: exact matches only. Close words are hidden.", exactOff: "Setting changed: close words will be shown, always labelled.",
  netErr: "Sorry, I couldn't reach the server. Please try again.",
  badge: { R0: "Info", R1: "Exact match", R2: "Exact match (same meaning)", R3: "Close word, not the same word", R4: "No sign we're sure of", R5: "Not something I do", R6: "Problem on our side", R7: "Needs a person" },
  whyBtn: "Why this result?", browseAct: "Browse the 56 words", quizAct: "Open the quiz", retry: "Try again", edit: "Edit word", over: "Start over",
  slow: "Slow 0.5×", normal: "Normal 1×", replay: "↻ Replay", speedLabel: "Video speed",
  videoLabel: (en, ar) => `Sign video: ${en} (${ar})`,
  helpful: "Helpful", notHelpful: "Not helpful", fbQ: "What went wrong?",
  reasons: ["Wrong sign", "Wrong word", "Hard to see", "Unclear explanation", "Other"], fbSend: "Send feedback",
  fbOk: "✓ Thank you! Our team reviews feedback every week.", fbFail: "Sorry, your feedback was not sent. Please try again.", altFail: "Sorry, I couldn't load other words. Please search again.",
  needPerson: "Need a person?", needPersonText: "Ask a qualified Egyptian Sign Language teacher or interpreter, or your local Deaf association.",
  urgent: "Get help now", urgentText: "Ambulance 123 · Police 122 (Egypt)",
  browseFail: "Could not load the word list. Is the backend running?",
  whyTitle: "Why this result?", inShort: "In short:", expert: "Details for experts",
  fullTrace: "Full decision trace", allChecks: "All checks in order", considered: "Words we compared",
  colEntry: "Word", colScore: "Similarity", colDecision: "Decision",
  whoModel: m => `Who wrote the reply? The AI model (${m}) only worded the sentence, and it was checked against what really happened. The video and result were chosen by our code, not the model.`,
  whoTemplate: "Who wrote the reply? A ready-written sentence by our team. The video and result were chosen by our code using its rules.",
  rows: { typed: "You typed", cleaned: "After cleaning", steps: "Cleaning", looked: "Word looked up", rule: "Rule", entry: "Dataset word", matched: "Matched on", video: "Video file", closest: "Closest word", thr: "Minimum similarity", setting: "Setting", safety: "Safety check", dataset: "Dataset", trace: "Trace id" },
  settingOn: "Exact matches only: ON", settingOff: "Exact matches only: off",
  pct: x => `${Math.round(x * 100)}%`,
  score: (s, n) => `Score: ${s} / ${n}`, qOf: (c, n) => `Question ${c} of ${n}`, qNum: c => `Question ${c}`,
  next: "Next question →", results: "See results →", watch: "Watch carefully, then choose the meaning.", qText: "What does this sign mean?",
  correctMark: "✓ Correct answer", yourMark: "✗ Your answer", correct: "✓ Correct! Great job!",
  wrong: (ar, en) => `✗ Not quite. The correct answer is “${en} · ${ar}”.`, quizWhy: (id) => `Why: this video is the dataset word “${id}”. The other options are other words from the same dataset.`,
  loading: "Loading quiz questions…", quizFail: "Unable to load the quiz. Please check that the backend is running.", tryAgain: "Try again",
  done: "🌟 Quiz completed!", perfect: "🏆 Perfect score!", scored: (s, n) => `You scored ${s} out of ${n}. Keep practising!`, newQuiz: "↻ New quiz", finished: "Quiz completed!",
  quizVideo: c => `Quiz sign video, question ${c}`
}};

/* plain-language story for the "Why this result?" panel, built only from the trace */
function story(t, L) {
  const ar = L === "ar";
  const r = (t.results || [])[0];
  const typed = t.extracted_word || t.input;
  const thr = Math.round((t.threshold || 0.7) * 100);
  const word = x => ar ? x.arabic : `${x.english} (${x.arabic})`;
  const cleaned = (t.normalization_steps || []).length > 0;
  const s = [];
  if (ar) s.push(`انت كتبت «${t.input}».`); else s.push(`You typed “${t.input}”.`);
  if (t.extracted_word) s.push(ar ? `فهمنا إنك عايز إشارة كلمة «${t.extracted_word}».` : `We understood you want the sign for “${t.extracted_word}”.`);
  if (cleaned && ["R1", "R2", "R3", "R4"].includes(t.rule))
    s.push(ar ? "نضّفنا الكتابة الأول (شلنا التشكيل والعلامات، ووحّدنا الحروف زي أ وا) علشان نقارن صح."
              : "We cleaned the text first (removed marks and punctuation, made letters consistent) so we can compare fairly.");
  switch (t.rule) {
    case "R1":
      s.push(ar ? `لقينا نفس الكلمة بالظبط في قائمة الـ56 كلمة: «${t.matched_text}».` : `We found the exact same word in our list of 56 words: “${t.matched_text}”.`);
      s.push(ar ? "علشان كده بنعرضلك الفيديو بتاعها، وعليه علامة «مطابقة تامة»." : "So we show you its video, with the label “Exact match”.");
      break;
    case "R2":
      s.push(ar ? `«${t.matched_text}» طريقة تانية بنقول بيها «${r.arabic}»، وفريقنا راجعها قبل كده.` : `“${t.matched_text}” is another way to say “${r.english}”, and our team checked it before.`);
      s.push(ar ? "علشان كده بنعرضلك فيديو «" + r.arabic + "»." : `So we show you the video for “${r.english}”.`);
      break;
    case "R3":
      if (t.confusable) {
        s.push(ar ? `الكلمة دي مش عندنا. بس فيه كلمة شكلها زيها: «${r.arabic}»، ومعناها مختلف.` : `We don't have this word. One word looks like it, “${word(r)}”, but it means something different.`);
        s.push(ar ? "بنوريهالك بس علشان تاخد بالك إنها مش نفس الكلمة." : "We show it only so you notice it is not the same word.");
      } else {
        s.push(ar ? "ملقيناش الكلمة بالظبط." : "We didn't find the exact word.");
        s.push(ar ? `لقينا كلمة مكتوبة شبهها: «${r.arabic}» بنسبة تشابه ${Math.round(r.score * 100)}%. إحنا بنعرض الكلمة القريبة بس لو التشابه ${thr}% أو أكتر.`
                  : `We found a word spelled like it: “${word(r)}”, ${Math.round(r.score * 100)}% similar. We only show close words that are ${thr}% similar or more.`);
        s.push(ar ? "دي كلمة تانية، فمتستخدمهاش مكان كلمتك." : "It is a different word, so don't use it as your word.");
      }
      break;
    case "R4":
      if (t.settings && t.settings.exact_matches_only)
        s.push(ar ? "ملقيناش الكلمة بالظبط، وانت قافل «الكلمات القريبة» من الإعدادات، فمش هنعرض حاجة." : "We didn't find the exact word, and you turned off close words, so we show nothing.");
      else {
        s.push(ar ? "ملقيناش الكلمة بالظبط." : "We didn't find the exact word.");
        if (t.best_candidate)
          s.push(ar ? `أقرب كلمة كانت تشابهها ${Math.round(t.best_candidate.score * 100)}% بس، وده أقل من ${thr}%.` : `The closest word was only ${Math.round(t.best_candidate.score * 100)}% similar, below ${thr}%.`);
        s.push(ar ? "علشان كده مش هنعرض أي فيديو، لأننا مش بنخمّن." : "So we show no video, because we don't guess.");
      }
      break;
    case "R5":
      s.push(ar ? "رسالتك مش طلب إشارة لكلمة، فمدورناش على فيديو." : "Your message isn't a request for a word's sign, so we didn't search for a video."); break;
    case "R0":
      s.push(ar ? "رسالتك كانت تحية أو طلب مساعدة أو اختبار." : "Your message was a greeting, a help request, or a quiz request."); break;
    case "R7": {
      const k = t.safety;
      const m = ar ? { emergency: "رسالتك فيها كلام عن خطر أو طوارئ.", interpretation: "رسالتك بتطلب ترجمة محادثة في موقف مهم.", abuse: "رسالتك بتطلب إشارات لإهانة حد.", privacy: "رسالتك كان فيها رقم تليفون أو إيميل، فشلناه قبل أي حاجة." }
                   : { emergency: "Your message mentions danger or an emergency.", interpretation: "Your message asks to interpret a conversation in an important situation.", abuse: "Your message asks for signs to insult someone.", privacy: "Your message had a phone number or email, so we removed it first." };
      s.push(m[k] || "");
      s.push(ar ? "في الحالة دي بنرد برسالة أمان ثابتة، ومش بنعرض إشارة." : "In this case we reply with a fixed safety message and show no sign.");
      break;
    }
  }
  return s;
}

/* ---------- state ---------- */
let L = "ar";
try { L = localStorage.getItem("comind_lang") || "ar"; } catch (e) {}
const t = k => T[L][k];
const messages = document.getElementById("messages");
const input = document.getElementById("userInput");
const quick = document.getElementById("quickPrompts");
const stagePill = document.getElementById("stagePill");
let lastMessage = "", userSearches = 0, stage = 1, serverInfo = null;

function el(tag, attrs = {}, ...children) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "text") n.textContent = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const c of children) if (c) n.append(c);
  return n;
}
function scrollDown() {
  requestAnimationFrame(() => {
    messages.scrollTop = messages.scrollHeight;
  });
}
function focusInput() { setTimeout(() => input.focus(), 50); }
function store(k, v) { try { localStorage.setItem("comind_" + k, v); } catch (e) {} }
function read(k) { try { return localStorage.getItem("comind_" + k); } catch (e) { return null; } }

/* ---------- language ---------- */
function applyLang() {
  document.documentElement.lang = L;
  document.documentElement.dir = L === "ar" ? "rtl" : "ltr";
  document.title = L === "ar" ? "إشارة | اتعلم لغة الإشارة المصرية" : "ISHARA | Learn Sign Language";
  document.querySelectorAll("[data-i18n]").forEach(n => { n.textContent = t(n.dataset.i18n); });
  document.querySelectorAll("[data-i18n-html]").forEach(n => { n.innerHTML = t(n.dataset.i18nHtml); });  /* our own fixed strings only */
  document.querySelectorAll("[data-i18n-attr]").forEach(n => {
    n.dataset.i18nAttr.split(";").forEach(pair => { const [a, k] = pair.split(":"); n.setAttribute(a, t(k)); });
  });
  document.getElementById("langBtn").textContent = t("langBtn");
  document.getElementById("langBtn").setAttribute("lang", L === "ar" ? "en" : "ar");
  renderHelp();
  setStage(stage);
  showConn();
  if (questions.length) renderQuestion();
}
function toggleLang() {
  L = L === "ar" ? "en" : "ar";
  store("lang", L);
  applyLang();
}

/* ---------- settings ---------- */
function setScale(s) {
  document.documentElement.style.setProperty("--scale", s);
  document.querySelectorAll(".size-buttons button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.scale === String(s))));
  store("scale", s);
}
document.querySelectorAll(".size-buttons button").forEach(b => b.addEventListener("click", () => setScale(b.dataset.scale)));
const hc = document.getElementById("highContrast");
hc.addEventListener("change", () => { document.body.classList.toggle("hc", hc.checked); store("hc", hc.checked ? "1" : "0"); });
const exactOnly = document.getElementById("exactOnly");
exactOnly.addEventListener("change", () => { store("exact", exactOnly.checked ? "1" : "0"); addStatus(exactOnly.checked ? t("exactOn") : t("exactOff")); });
if (read("scale")) setScale(read("scale"));
if (read("hc") === "1") { hc.checked = true; document.body.classList.add("hc"); }
if (read("exact") === "1") exactOnly.checked = true;

document.addEventListener("keydown", e => {
  if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
});

/* ---------- onboarding ---------- */
function setChips(label, items) {
  quick.replaceChildren(el("span", { class: "quick-label", text: label }));
  for (const w of items) {
    const b = el("button", { type: "button", text: w.text || w, dir: "auto" });
    b.addEventListener("click", w.action || (() => ask(w)));
    quick.append(b);
  }
}
function setStage(n) {
  stage = n;
  stagePill.textContent = t("stage" + n);
  if (n === 1) setChips(t("chips1"), [{ text: t("chipExample"), action: runExample }, ...t("words1")]);
  if (n === 2) setChips(t("chips2"), t("words2"));
  if (n === 3) setChips(t("chips3"), [...t("words3"), { text: t("chipBrowse"), action: openBrowse }, { text: t("chipQuiz"), action: openQuiz }]);
}
function greet() {
  const box = el("div", { class: "message bot-message" });
  t("greet").forEach(g => box.append(el("p", { style: "margin:0 0 6px", text: g })));
  box.append(el("ul", {}, el("li", { text: t("can") }), el("li", { text: t("cant") }), el("li", { text: t("why") })));
  messages.append(box);
  setStage(1);
}
async function runExample() {
  addStatus(t("exampleStatus"));
  await ask(L === "ar" ? "صباح الخير" : "Good morning", { example: true });
  addBot(t("exampleAfter"));
  setStage(2);
}

/* ---------- messages ---------- */
function addUser(text) { messages.append(el("div", { class: "message user-message", dir: "auto", text })); scrollDown(); }
function addBot(text) { messages.append(el("div", { class: "message bot-message", dir: "auto", text })); scrollDown(); }
function addStatus(text) { const n = el("div", { class: "message status-message", role: "status", text }); messages.append(n); scrollDown(); return n; }

document.getElementById("chatForm").addEventListener("submit", e => {
  e.preventDefault();
  const word = input.value.trim();
  if (!word) return;
  input.value = "";
  ask(word);
});

async function ask(word, opts = {}) {
  lastMessage = word;
  addUser(word);
  const status = addStatus(t("searching"));
  try {
    const res = await fetch(API + "/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: word, exact_only: exactOnly.checked, lang: L, simulate_error: !!opts.simulateError })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    status.remove();
    renderAnswer(data);
  } catch (err) {
    status.remove();
    renderAnswer({ rule: "R6", results: [], actions: ["retry", "edit", "start_over"], reply: t("netErr"), trace: null });
  }
  if (!opts.example) {
    userSearches++;
    if (stage === 1) setStage(2);
    else if (stage === 2 && userSearches >= 3) { setStage(3); addBot(t("stage3Msg")); }
  }
}

/* ---------- answers ---------- */
const ICONS = { R0: "i", R1: "✓", R2: "✓", R3: "≈", R4: "∅", R5: "?", R6: "!", R7: "⚠" };
function badgeEl(rule) {
  return el("span", { class: "badge badge-" + rule },
    el("span", { class: "ico", "aria-hidden": "true", text: ICONS[rule] }), el("span", { text: t("badge")[rule] }));
}

function renderAnswer(data) {
  const box = el("div", { class: "message bot-message" });
  box.append(badgeEl(data.rule));
  box.append(el("p", { dir: "auto", style: "margin:8px 0 0", text: data.reply }));
  for (const r of data.results || []) box.append(resultCard(data, r));

  const acts = el("div", { class: "result-actions" });
  let panel = null;
  if (data.trace) {
    const panelId = "why-" + data.trace_id;
    const why = el("button", { type: "button", class: "why-btn", "aria-expanded": "false", "aria-controls": panelId, text: t("whyBtn") });
    panel = whyPanel(data, panelId);
    panel.hidden = true;
    why.addEventListener("click", () => {
      panel.hidden = !panel.hidden;
      why.setAttribute("aria-expanded", String(!panel.hidden));
      if (!panel.hidden) panel.querySelector("h4").focus();
    });
    acts.append(why);
  }
  const A = data.actions || [];
  if (A.includes("not_what_i_meant")) acts.append(el("button", { type: "button", text: t("notMeant"), onclick: () => notWhatIMeant(data.trace_id) }));
  if (A.includes("browse")) acts.append(el("button", { type: "button", text: t("browseAct"), onclick: openBrowse }));
  if (A.includes("open_quiz")) acts.append(el("button", { type: "button", text: t("quizAct"), onclick: openQuiz }));
  if (data.rule === "R6") {
    acts.append(el("button", { type: "button", text: t("retry"), onclick: () => ask(lastMessage) }));
    acts.append(el("button", { type: "button", text: t("edit"), onclick: () => { input.value = lastMessage; input.focus(); } }));
    acts.append(el("button", { type: "button", text: t("over"), onclick: startOver }));
  }
  if (data.trace && ["R1", "R2", "R3", "R4"].includes(data.rule)) acts.append(feedbackRow(data.trace_id, box));
  box.append(acts);
  if (panel) box.append(panel);
  if (A.includes("handover")) box.append(handoverBox(data));
  messages.append(box);
  scrollDown();
}

function addFullscreenButton(video, controls) {
  const button = el("button", { type: "button", text: L === "ar" ? "ملء الشاشة ⛶" : "Fullscreen ⛶", class: "video-fullscreen", "aria-label": L === "ar" ? "فتح الفيديو بملء الشاشة" : "Open video fullscreen" });
  button.addEventListener("click", () => {
    if (video.requestFullscreen) video.requestFullscreen();
    else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
  });
  controls.append(button);
}

function resultCard(data, r) {
  const card = el("div", { class: "result-card" });
  card.append(el("div", { class: "entry-label" },
    el("span", { class: "ar", lang: "ar", dir: "rtl", text: r.arabic }), " · ", el("span", { lang: "en", dir: "ltr", text: r.english })));
  if (data.rule === "R3" && r.reason) card.append(el("p", { class: "related-reason", dir: "auto", text: r.reason }));
  else if (r.note) card.append(el("p", { class: "entry-note", dir: "auto", text: r.note }));
  const v = el("video", { controls: "", preload: "metadata", playsinline: "", "aria-label": t("videoLabel")(r.english, r.arabic) });
  v.addEventListener("loadedmetadata", scrollDown, { once: true });
  v.src = API + r.video_url;
  card.append(v);
  const ctr = el("div", { class: "video-controls", role: "group", "aria-label": t("speedLabel") });
  for (const [k, rate] of [["slow", 0.5], ["normal", 1]]) {
    const b = el("button", { type: "button", text: t(k), "aria-pressed": String(rate === 1) });
    b.addEventListener("click", () => {
      v.playbackRate = rate;
      ctr.querySelectorAll("button[aria-pressed]").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
      v.play().catch(() => {});
    });
    ctr.append(b);
  }
  ctr.append(el("button", { type: "button", text: t("replay"), onclick: () => { v.currentTime = 0; v.play().catch(() => {}); } }));
  addFullscreenButton(v, ctr);
  card.append(ctr);
  return card;
}

function whyPanel(data, id) {
  const tr = data.trace, R = t("rows");
  const p = el("section", { class: "why-panel", id, "aria-label": t("whyTitle") });
  p.append(el("h4", { tabindex: "-1", text: t("whyTitle") }));
  p.append(el("p", { class: "in-short", text: t("inShort") }));
  const ol = el("ol", { class: "story" });
  story(tr, L).forEach(line => ol.append(el("li", { dir: "auto", text: line })));
  p.append(ol);
  p.append(el("p", { class: "who", text: tr.reply_source === "model" ? t("whoModel")(tr.model.model) : t("whoTemplate") }));

  const ex = el("details", { class: "expert" }, el("summary", { text: t("expert") }));
  const dl = el("dl");
  const row = (k, v) => { if (v !== undefined && v !== null && v !== "") dl.append(el("dt", { text: k }), el("dd", { dir: "auto", text: v })); };
  row(R.typed, tr.input);
  row(R.cleaned, tr.normalized);
  if (tr.normalization_steps && tr.normalization_steps.length) row(R.steps, tr.normalization_steps.map(s => s.step).join("; "));
  row(R.looked, tr.extracted_word);
  row(R.rule, `${tr.rule} · ${tr.rule_name}`);
  const first = (tr.results || [])[0];
  if (first && ["R1", "R2"].includes(tr.rule)) {
    row(R.entry, `${first.id} (${first.arabic} · ${first.english})`);
    row(R.matched, `${tr.matched_field}: “${tr.matched_text}”`);
    row(R.video, first.video);
  }
  if (tr.rule === "R4" && tr.best_candidate) row(R.closest, `${tr.best_candidate.label} · ${t("pct")(tr.best_candidate.score)}`);
  if (["R3", "R4"].includes(tr.rule)) row(R.thr, `${t("pct")(tr.threshold)} (T = ${tr.threshold}) · ${tr.similarity_method}`);
  row(R.setting, tr.settings && tr.settings.exact_matches_only ? t("settingOn") : t("settingOff"));
  if (tr.safety) row(R.safety, tr.safety);
  row(R.dataset, tr.dataset);
  row(R.trace, `${tr.trace_id} · ${tr.engine_version} · ${tr.model ? tr.model.status : ""} · ${tr.total_ms} ms`);
  ex.append(dl);
  if (tr.candidates && tr.candidates.length) {
    const tbl = el("table");
    tbl.append(el("caption", { text: t("considered") }));
    tbl.append(el("thead", {}, el("tr", {}, el("th", { scope: "col", text: t("colEntry") }), el("th", { scope: "col", text: t("colScore") }), el("th", { scope: "col", text: t("colDecision") }))));
    const tb = el("tbody");
    for (const c of tr.candidates)
      tb.append(el("tr", {}, el("td", { dir: "auto", text: c.label || c.id }), el("td", { text: c.score == null ? "–" : t("pct")(c.score) }), el("td", { dir: "ltr", text: `${c.decision} (${c.reason})` })));
    tbl.append(tb);
    ex.append(tbl);
  }
  if (tr.checks && tr.checks.length) {
    const d = el("details", {}, el("summary", { text: t("allChecks") }));
    const ol2 = el("ol", { dir: "ltr" });
    for (const c of tr.checks) ol2.append(el("li", { dir: "auto", text: `${c.check}: ${c.outcome}${c.detail ? " — " + c.detail : ""}` }));
    d.append(ol2); ex.append(d);
  }
  ex.append(el("details", {}, el("summary", { text: t("fullTrace") }), el("pre", { dir: "ltr", text: JSON.stringify(tr, null, 2) })));
  p.append(ex);
  return p;
}

function feedbackRow(traceId, box) {
  const wrap = el("div", { class: "feedback-row", role: "group" });
  const up = el("button", { type: "button", "aria-pressed": "false", "aria-label": t("helpful"), text: "👍" });
  const down = el("button", { type: "button", "aria-pressed": "false", "aria-label": t("notHelpful"), text: "👎" });
  up.addEventListener("click", () => { up.setAttribute("aria-pressed", "true"); down.setAttribute("aria-pressed", "false"); sendFeedback(traceId, "up", null, box); });
  down.addEventListener("click", () => {
    down.setAttribute("aria-pressed", "true"); up.setAttribute("aria-pressed", "false");
    if (box.querySelector(".reason-box")) return;
    const fs = el("fieldset", {}, el("legend", { text: t("fbQ") }));
    t("reasons").forEach((r, i) => {
      const rid = `r-${traceId}-${i}`;
      fs.append(el("label", { for: rid }, el("input", { type: "radio", name: "reason-" + traceId, id: rid, value: T.en.reasons[i] }), " " + r));
    });
    const send = el("button", { type: "button", class: "btn btn-small btn-primary", text: t("fbSend") });
    const rb = el("div", { class: "reason-box" }, fs, send);
    send.addEventListener("click", () => { const ch = rb.querySelector("input:checked"); sendFeedback(traceId, "down", ch ? ch.value : null, box); rb.remove(); });
    box.append(rb);
    fs.querySelector("input").focus();
  });
  wrap.append(up, down);
  return wrap;
}
async function sendFeedback(traceId, vote, reason, box) {
  try {
    await fetch(API + "/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ trace_id: traceId, vote, reason }) });
    box.append(el("p", { role: "status", style: "margin:6px 0 0;font-size:.9rem", text: t("fbOk") }));
  } catch (e) { box.append(el("p", { role: "status", text: t("fbFail") })); }
}
async function notWhatIMeant(traceId) {
  addUser(t("notMeant"));
  const status = addStatus(t("lookingOther"));
  try {
    const r = await fetch(API + "/alternatives", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ trace_id: traceId, lang: L }) });
    const d = await r.json();
    status.remove();
    if (!r.ok) throw new Error(d.detail);
    renderAnswer(d);
  } catch (e) { status.remove(); addBot(t("altFail")); }
}
function handoverBox(data) {
  const b = el("div", { class: "handover-box", role: "note" });
  if (data.trace && data.trace.safety === "emergency") b.append(el("strong", { text: t("urgent") }), el("span", { text: t("urgentText") }));
  else b.append(el("strong", { text: t("needPerson") }), el("span", { text: t("needPersonText") }));
  return b;
}
function startOver() { messages.replaceChildren(); userSearches = 0; greet(); focusInput(); }

/* ---------- help / browse ---------- */
function renderHelp() {
  const ar = L === "ar";
  const body = document.getElementById("helpBody");
  const H = (x) => el("h3", { text: x });
  const ul = (...items) => { const u = el("ul"); items.forEach(i => u.append(i instanceof Node ? i : el("li", { text: i }))); return u; };
  const badgeLi = (rule, txt) => el("li", {}, badgeEl(rule), " " + txt);
  body.replaceChildren(
    H(ar ? "العلامات معناها إيه؟" : "What the labels mean"),
    ul(badgeLi("R1", ar ? "الفيديو ده هو إشارة كلمتك بالظبط." : "The video is the sign for your exact word."),
       badgeLi("R3", ar ? "كلمة تانية شكلها شبه كلمتك. متستخدمهاش مكان كلمتك." : "A different word that looks similar. Don't use it as your word."),
       badgeLi("R4", ar ? "معندناش فيديو متأكدين منه، ومش هنخمّن." : "We have no video we're sure of. We won't guess."),
       badgeLi("R7", ar ? "اسأل مترجم أو مدرس متخصص، أو اطلب مساعدة." : "Ask a qualified interpreter or teacher, or call for help.")),
    H(ar ? "«إشارة» يقدر يعمل إيه؟" : "What Ishara can and cannot do"),
    ul(t("can"), t("cant")),
    H(ar ? "الإجابات جاية منين؟" : "Where the answers come from"),
    ul(ar ? "الفيديوهات: من داتا عامة على Kaggle اسمها Egyptian Sign Language Recognition، عملها عبدالله شردي و Eng Sira. فيها 56 كلمة و477 فيديو، وإحنا بنعرض فيديو واحد لكل كلمة. الصفحة مش كاتبة رخصة، فبنستخدمها بس في مشروع الكلية ومش بنبيعها."
           : "Videos: the public Egyptian Sign Language Recognition dataset on Kaggle by Abdullah Sherdy and Eng Sira (56 words, 477 videos; we show one video per word). The page states no license, so we use it only for this non-commercial course project.",
       ar ? "المعاني بالعربي والإنجليزي كتبها فريقنا من أسماء الملفات في الداتا." : "The Arabic and English meanings were written by our team from the dataset folder names.",
       ar ? "نموذج الذكاء الاصطناعي (Qwen2.5-7B-Instruct) بيصيغ الجملة بس. مش هو اللي بيختار الفيديو، وكل رد بيتراجع على اللي حصل فعلاً."
          : "The AI model (Qwen2.5-7B-Instruct) only words the sentence. It never picks the video, and every reply is checked against what really happened."),
    H(ar ? "الكيبورد" : "Keyboard"),
    el("p", { text: ar ? "/ يوديك لمربع الكتابة · Enter يبعت · Esc يقفل الشباك ده." : "/ jumps to the search box · Enter sends · Esc closes this window." })
  );
}
let signsCache = null;
async function openBrowse() {
  const dlg = document.getElementById("browseDialog");
  const grid = document.getElementById("wordGrid");
  if (!signsCache) {
    try { signsCache = (await (await fetch(API + "/signs")).json()).signs; }
    catch (e) { grid.textContent = t("browseFail"); }
  }
  if (signsCache) {
    const list = [...signsCache].sort((a, b) => L === "ar" ? a.arabic.localeCompare(b.arabic, "ar") : a.english.localeCompare(b.english));
    grid.replaceChildren(...list.map(s => {
      const b = el("button", { type: "button" },
        el("strong", { dir: "auto", text: L === "ar" ? s.arabic : s.english }), el("span", { dir: "auto", text: L === "ar" ? s.english : s.arabic }));
      b.addEventListener("click", () => { dlg.close(); ask(L === "ar" ? s.arabic : s.english); });
      return b;
    }));
  }
  dlg.showModal();
}
function openHelp() { document.getElementById("helpDialog").showModal(); }
function openQuiz() { document.querySelector("#quiz").scrollIntoView(); setTimeout(() => document.querySelector("#quizContent button")?.focus(), 400); }

function showConn() {
  const c = document.getElementById("connStatus");
  if (serverInfo === null) c.textContent = "…";
  else if (serverInfo === false) c.textContent = t("connFail");
  else c.textContent = t("conn")(serverInfo.total_signs) + (serverInfo.model_enabled ? t("connModelOn") : t("connModelOff"));
}
fetch(API + "/").then(r => r.json()).then(d => { serverInfo = d; showConn(); }).catch(() => { serverInfo = false; showConn(); });

/* ---------------------------------------------------------------
   QUIZ: questions and options are built by the backend from the index
---------------------------------------------------------------- */
let questions = [], current = 0, score = 0, answered = false, chosen = null;

async function loadQuiz() {
  const content = document.getElementById("quizContent");
  try {
    content.textContent = t("loading");
    const response = await fetch(API + "/quiz?n=5");
    if (!response.ok) throw new Error();
    const data = await response.json();
    if (data.status !== "success" || !data.questions.length) throw new Error();
    questions = data.questions.map(q => ({ ...q, video: API + q.video_url, correct: q.options.findIndex(o => o.id === q.id) }));
    current = 0; score = 0;
    renderQuestion();
  } catch (error) {
    content.replaceChildren(el("p", { text: t("quizFail") }), el("button", { class: "btn btn-light", type: "button", text: t("tryAgain"), onclick: loadQuiz }));
  }
}

function renderQuestion() {
  answered = false; chosen = null;
  const q = questions[current];
  const content = document.getElementById("quizContent");
  const nextBtn = document.getElementById("nextBtn");
  content.replaceChildren();
  nextBtn.disabled = true;
  nextBtn.style.display = "inline-block";
  nextBtn.textContent = current === questions.length - 1 ? t("results") : t("next");
  document.getElementById("scorePill").textContent = t("score")(score, questions.length);
  document.getElementById("quizStatus").textContent = t("qOf")(current + 1, questions.length);
  document.getElementById("progressBar").style.width = `${(score / questions.length) * 100}%`;
  document.getElementById("progress").setAttribute("aria-valuenow", score);
  content.append(el("div", { class: "question-count", text: t("qNum")(current + 1) }));
  const video = el("video", { class: "quiz-video", controls: "", preload: "metadata", playsinline: "", "aria-label": t("quizVideo")(current + 1) });
  video.src = q.video;
  const ctr = el("div", { class: "video-controls" },
    el("button", { type: "button", text: t("slow"), onclick: () => { video.playbackRate = 0.5; video.play().catch(() => {}); } }),
    el("button", { type: "button", text: t("normal"), onclick: () => { video.playbackRate = 1; video.play().catch(() => {}); } }),
    el("button", { type: "button", text: t("replay"), onclick: () => { video.currentTime = 0; video.play().catch(() => {}); } }));
  addFullscreenButton(video, ctr);
  content.append(el("div", { class: "quiz-video-box" }, video, ctr, el("div", { class: "quiz-video-label", text: t("watch") })));
  content.append(el("div", { class: "question", id: "qtext", text: t("qText") }));
  const answers = el("div", { class: "answers", role: "group", "aria-labelledby": "qtext" });
  q.options.forEach((option, index) => {
    const button = el("button", { type: "button", class: "answer" },
      el("span", { class: "answer-letter", "aria-hidden": "true", text: L === "ar" ? "أبجد"[index] : "ABCD"[index] }),
      el("span", { lang: "ar", dir: "rtl", text: option.arabic }),
      el("span", { lang: "en", dir: "ltr", text: " · " + option.english }),
      el("span", { class: "mark" }));
    button.addEventListener("click", () => chooseAnswer(index));
    answers.appendChild(button);
  });
  content.append(answers);
  content.append(el("div", { class: "feedback", id: "feedback", role: "status" }));
}

function chooseAnswer(index) {
  if (answered) return;
  answered = true; chosen = index;
  const q = questions[current];
  const buttons = document.querySelectorAll("#quizContent .answer");
  const feedback = document.getElementById("feedback");
  buttons.forEach(b => b.disabled = true);
  buttons[q.correct].classList.add("correct");
  buttons[q.correct].querySelector(".mark").textContent = t("correctMark");
  if (index === q.correct) {
    score++;
    feedback.replaceChildren(el("span", { text: t("correct") }));
    feedback.style.color = "#166534";
  } else {
    buttons[index].classList.add("wrong");
    buttons[index].querySelector(".mark").textContent = t("yourMark");
    feedback.replaceChildren(el("span", { text: t("wrong")(q.arabic, q.english) }));
    feedback.style.color = "#b42318";
  }
  feedback.append(el("small", { text: t("quizWhy")(L === "ar" ? q.arabic : q.english) }));
  document.getElementById("scorePill").textContent = t("score")(score, questions.length);
  document.getElementById("progressBar").style.width = `${(score / questions.length) * 100}%`;
  document.getElementById("progress").setAttribute("aria-valuenow", score);
  const nb = document.getElementById("nextBtn");
  nb.disabled = false; nb.focus();
}
function nextQuestion() {
  if (!answered) return;
  if (current < questions.length - 1) { current++; renderQuestion(); } else showResults();
}
function showResults() {
  const content = document.getElementById("quizContent");
  content.replaceChildren();
  document.getElementById("progressBar").style.width = `${(score / questions.length) * 100}%`;
  document.getElementById("progress").setAttribute("aria-valuenow", score);
  document.getElementById("quizStatus").textContent = t("finished");
  document.getElementById("scorePill").textContent = t("score")(score, questions.length);
  content.append(el("h3", { tabindex: "-1", text: score === questions.length ? t("perfect") : t("done") }));
  content.append(el("p", { text: t("scored")(score, questions.length) }));
  content.append(el("button", { class: "btn btn-primary", type: "button", text: t("newQuiz"), onclick: loadQuiz }));
  document.getElementById("nextBtn").style.display = "none";
  content.querySelector("h3").focus();
}

applyLang();
greet();
loadQuiz();

const chatbox = document.getElementById("chatbox");
const chatMaximize = document.getElementById("chatMaximize");
chatMaximize.addEventListener("click", () => {
  const maximized = chatbox.classList.toggle("maximized");
  chatMaximize.textContent = maximized ? "×" : "⛶";
  chatMaximize.setAttribute("aria-label", maximized ? (L === "ar" ? "إغلاق العرض المكبر" : "Close maximized chat") : (L === "ar" ? "تكبير نافذة المحادثة" : "Maximize chat"));
  if (maximized) document.body.style.overflow = "hidden";
  else document.body.style.overflow = "";
});
