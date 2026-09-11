/* ============================================================
   GARUDA AI
   Personal Cyber Safety Agent
   Frontend
   ============================================================ */


/* ============================================================
   CONFIG
============================================================ */

const API_URL =
    "http://127.0.0.1:8000";

const MAX_MESSAGE_LENGTH =
    5000;

const MAX_IMAGE_SIZE =
    10 * 1024 * 1024;

const ALLOWED_IMAGE_TYPES = [
    "image/png",
    "image/jpeg",
    "image/webp"
];


/* ============================================================
   STATE
============================================================ */

let selectedScreenshot =
    null;

let selectedScreenshotUrl =
    null;

let isAnalyzing =
    false;


/* ============================================================
   DOM
============================================================ */

const messageMode =
    document.getElementById(
        "message-mode"
    );

const screenshotMode =
    document.getElementById(
        "screenshot-mode"
    );

const messageInputArea =
    document.getElementById(
        "message-input-area"
    );

const screenshotInputArea =
    document.getElementById(
        "screenshot-input-area"
    );

const message =
    document.getElementById(
        "message"
    );

const charCount =
    document.getElementById(
        "char-count"
    );

const analyzeButton =
    document.getElementById(
        "analyze-button"
    );

const screenshotInput =
    document.getElementById(
        "screenshot-input"
    );

const screenshotUploadArea =
    document.getElementById(
        "screenshot-upload-area"
    );

const uploadPlaceholder =
    document.getElementById(
        "upload-placeholder"
    );

const chooseScreenshotButton =
    document.getElementById(
        "choose-screenshot-button"
    );

const imagePreviewContainer =
    document.getElementById(
        "image-preview-container"
    );

const imagePreview =
    document.getElementById(
        "image-preview"
    );

const removeImageButton =
    document.getElementById(
        "remove-image"
    );

const analyzeScreenshotButton =
    document.getElementById(
        "analyze-screenshot-button"
    );

const screenshotStatus =
    document.getElementById(
        "screenshot-status"
    );

const ocrLanguage =
    document.getElementById(
        "ocr-language"
    );

const ocrResultCard =
    document.getElementById(
        "ocr-result-card"
    );

const ocrExtractedText =
    document.getElementById(
        "ocr-extracted-text"
    );

const loading =
    document.getElementById(
        "loading"
    );

const loadingMessage =
    document.getElementById(
        "loading-message"
    );

const result =
    document.getElementById(
        "result"
    );

const error =
    document.getElementById(
        "error"
    );

const errorMessage =
    document.getElementById(
        "error-message"
    );

const errorDismiss =
    document.getElementById(
        "error-dismiss"
    );

const newScanButton =
    document.getElementById(
        "new-scan-button"
    );


/* ============================================================
   RESULT DOM
============================================================ */

const fraudTypeElement =
    document.getElementById(
        "fraud-type"
    );

const riskScoreElement =
    document.getElementById(
        "risk-score"
    );

const riskLevelElement =
    document.getElementById(
        "risk-level"
    );

const riskBarFill =
    document.getElementById(
        "risk-bar-fill"
    );

const confidenceElement =
    document.getElementById(
        "confidence"
    );

const confidenceBarFill =
    document.getElementById(
        "confidence-bar-fill"
    );

const signalsElement =
    document.getElementById(
        "signals"
    );

const attackerGoalElement =
    document.getElementById(
        "attacker-goal"
    );

const recommendedActionElement =
    document.getElementById(
        "recommended-action"
    );

const evidenceList =
    document.getElementById(
        "evidence-list"
    );

const traceList =
    document.getElementById(
        "trace-list"
    );

const escalationCard =
    document.getElementById(
        "escalation-card"
    );

const escalationReasons =
    document.getElementById(
        "escalation-reasons"
    );

const resultStatusBadge =
    document.getElementById(
        "result-status-badge"
    );


/*
    Optional risk breakdown element.

    This is intentionally optional so the frontend continues
    working even before the corresponding HTML is added.
*/
const riskBreakdownElement =
    document.getElementById(
        "risk-breakdown"
    );


/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    initializeApp
);


function initializeApp() {

    setupModeButtons();

    setupMessageInput();

    setupScreenshotInput();

    setupErrorHandling();

    setupResetButton();

    updateCharacterCount();

    console.log(
        "Garuda AI frontend initialized."
    );

    console.log(
        "Tesseract available:",
        typeof Tesseract !== "undefined"
    );

}


/* ============================================================
   MODE BUTTONS
============================================================ */

function setupModeButtons() {

    if (messageMode) {

        messageMode.addEventListener(
            "click",
            () => switchMode("message")
        );

    }


    if (screenshotMode) {

        screenshotMode.addEventListener(
            "click",
            () => switchMode("screenshot")
        );

    }

}


function switchMode(mode) {

    hideError();

    hideResult();

    hideLoading();


    if (mode === "message") {

        messageMode.classList.add(
            "active"
        );

        screenshotMode.classList.remove(
            "active"
        );

        messageInputArea.classList.remove(
            "hidden"
        );

        screenshotInputArea.classList.add(
            "hidden"
        );

    } else {

        messageMode.classList.remove(
            "active"
        );

        screenshotMode.classList.add(
            "active"
        );

        messageInputArea.classList.add(
            "hidden"
        );

        screenshotInputArea.classList.remove(
            "hidden"
        );

    }

}


/* ============================================================
   MESSAGE
============================================================ */

function setupMessageInput() {

    if (!message) {
        return;
    }


    message.addEventListener(
        "input",
        updateCharacterCount
    );


    if (analyzeButton) {

        analyzeButton.addEventListener(
            "click",
            handleMessageAnalysis
        );

    }


    message.addEventListener(
        "keydown",
        event => {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                handleMessageAnalysis();

            }

        }
    );

}


function updateCharacterCount() {

    if (
        !message ||
        !charCount
    ) {
        return;
    }


    const length =
        message.value.length;


    charCount.textContent =
        `${length} / ${MAX_MESSAGE_LENGTH}`;


    if (
        length >=
        MAX_MESSAGE_LENGTH * 0.9
    ) {

        charCount.style.color =
            "#ff9b62";

    } else {

        charCount.style.color =
            "";

    }

}


/* ============================================================
   MESSAGE ANALYSIS
============================================================ */

async function handleMessageAnalysis() {

    if (isAnalyzing) {
        return;
    }


    const text =
        message.value.trim();


    if (!text) {

        showError(
            "Please enter a suspicious message before analyzing."
        );

        return;

    }


    if (
        text.length >
        MAX_MESSAGE_LENGTH
    ) {

        showError(
            "The message is too long. Maximum length is 5000 characters."
        );

        return;

    }


    await runAnalysis(
        text,
        "message"
    );

}


/* ============================================================
   SCREENSHOT SETUP
============================================================ */

function setupScreenshotInput() {

    if (!screenshotInput) {
        return;
    }


    /*
        IMPORTANT:

        We intentionally DO NOT attach a click handler
        to chooseScreenshotButton.

        It is a <label for="screenshot-input">.

        The browser automatically opens the native
        file picker when the label is clicked.
    */


    screenshotInput.addEventListener(
        "change",
        handleScreenshotSelection
    );


    if (removeImageButton) {

        removeImageButton.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                removeScreenshot();

            }
        );

    }


    if (analyzeScreenshotButton) {

        analyzeScreenshotButton.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                handleScreenshotAnalysis();

            }
        );

    }


    /*
        Clicking empty upload area also opens
        the file picker.
    */

    if (screenshotUploadArea) {

        screenshotUploadArea.addEventListener(
            "click",
            event => {

                /*
                    Do nothing if the user clicked
                    the choose label itself.
                */

                if (
                    event.target.closest(
                        "#choose-screenshot-button"
                    )
                ) {

                    return;

                }


                /*
                    Do nothing when clicking preview.
                */

                if (
                    event.target.closest(
                        "#image-preview-container"
                    )
                ) {

                    return;

                }


                screenshotInput.click();

            }
        );

    }


    /*
        Drag and drop.
    */

    if (screenshotUploadArea) {

        screenshotUploadArea.addEventListener(
            "dragover",
            event => {

                event.preventDefault();

                screenshotUploadArea.style.borderColor =
                    "rgba(100, 150, 255, 0.65)";

            }
        );


        screenshotUploadArea.addEventListener(
            "dragleave",
            () => {

                screenshotUploadArea.style.borderColor =
                    "";

            }
        );


        screenshotUploadArea.addEventListener(
            "drop",
            event => {

                event.preventDefault();

                screenshotUploadArea.style.borderColor =
                    "";


                const files =
                    event.dataTransfer.files;


                if (
                    files &&
                    files.length > 0
                ) {

                    processScreenshotFile(
                        files[0]
                    );

                }

            }
        );

    }

}


/* ============================================================
   SCREENSHOT SELECTION
============================================================ */

function handleScreenshotSelection(
    event
) {

    const file =
        event.target.files &&
        event.target.files[0];


    if (!file) {
        return;
    }


    processScreenshotFile(
        file
    );

}


function processScreenshotFile(
    file
) {

    hideError();


    if (
        !ALLOWED_IMAGE_TYPES.includes(
            file.type
        )
    ) {

        showError(
            "Unsupported image format. Please use PNG, JPG, or WEBP."
        );

        resetScreenshotInput();

        return;

    }


    if (
        file.size >
        MAX_IMAGE_SIZE
    ) {

        showError(
            "The screenshot is too large. Maximum file size is 10 MB."
        );

        resetScreenshotInput();

        return;

    }


    selectedScreenshot =
        file;


    if (
        selectedScreenshotUrl
    ) {

        URL.revokeObjectURL(
            selectedScreenshotUrl
        );

    }


    selectedScreenshotUrl =
        URL.createObjectURL(
            file
        );


    imagePreview.src =
        selectedScreenshotUrl;


    imagePreview.onload =
        () => {

            imagePreviewContainer.classList.remove(
                "hidden"
            );

            uploadPlaceholder.classList.add(
                "hidden"
            );

        };


    analyzeScreenshotButton.disabled =
        false;


    screenshotStatus.textContent =
        `Screenshot ready: ${file.name}`;


    screenshotStatus.style.color =
        "#79dcae";


    hideOCRResult();

}


/* ============================================================
   REMOVE SCREENSHOT
============================================================ */

function removeScreenshot() {

    selectedScreenshot =
        null;


    if (
        selectedScreenshotUrl
    ) {

        URL.revokeObjectURL(
            selectedScreenshotUrl
        );

        selectedScreenshotUrl =
            null;

    }


    imagePreview.removeAttribute(
        "src"
    );


    imagePreviewContainer.classList.add(
        "hidden"
    );


    uploadPlaceholder.classList.remove(
        "hidden"
    );


    analyzeScreenshotButton.disabled =
        true;


    screenshotStatus.textContent =
        "Ready for screenshot OCR.";


    screenshotStatus.style.color =
        "";


    resetScreenshotInput();

    hideOCRResult();

}


function resetScreenshotInput() {

    if (screenshotInput) {

        screenshotInput.value =
            "";

    }

}


/* ============================================================
   SCREENSHOT OCR
============================================================ */

async function handleScreenshotAnalysis() {

    if (isAnalyzing) {
        return;
    }


    if (!selectedScreenshot) {

        showError(
            "Please choose a screenshot first."
        );

        return;

    }


    if (
        typeof Tesseract ===
        "undefined"
    ) {

        showError(
            "OCR engine could not be loaded. Please refresh the page and check your internet connection."
        );

        return;

    }


    try {

        isAnalyzing =
            true;


        setScreenshotControlsDisabled(
            true
        );


        hideError();

        hideResult();

        hideOCRResult();


        showLoading(
            "Reading the screenshot with local OCR..."
        );


        const language =
            ocrLanguage
                ? ocrLanguage.value
                : "eng";


        screenshotStatus.textContent =
            "Starting OCR engine...";


        const ocrResult =
            await Tesseract.recognize(
                selectedScreenshot,
                language,
                {
                    logger:
                        handleOCRProgress
                }
            );


        const extractedText =
            ocrResult &&
            ocrResult.data &&
            ocrResult.data.text
                ? ocrResult.data.text.trim()
                : "";


        if (!extractedText) {

            throw new Error(
                "No readable text was found in the screenshot. Please upload a clearer screenshot."
            );

        }


        /*
            SHOW OCR OUTPUT
        */

        displayOCRResult(
            extractedText
        );


        screenshotStatus.textContent =
            "OCR completed successfully.";


        screenshotStatus.style.color =
            "#79dcae";


        /*
            SEND OCR TEXT TO THE SAME
            GARUDA AI BACKEND PIPELINE.
        */

        await runAnalysis(
            extractedText,
            "screenshot"
        );


    } catch (err) {

        console.error(
            "Screenshot OCR error:",
            err
        );


        hideLoading();


        showError(
            getReadableError(
                err,
                "Unable to read the screenshot."
            )
        );

    } finally {

        isAnalyzing =
            false;


        setScreenshotControlsDisabled(
            false
        );

    }

}


/* ============================================================
   OCR PROGRESS
============================================================ */

function handleOCRProgress(
    progress
) {

    if (!progress) {
        return;
    }


    if (
        progress.status ===
        "recognizing text"
    ) {

        const percentage =
            Math.round(
                (
                    progress.progress ||
                    0
                ) * 100
            );


        screenshotStatus.textContent =
            `Reading screenshot... ${percentage}%`;


        showLoading(
            `OCR is reading the screenshot... ${percentage}%`
        );

    } else if (
        progress.status
    ) {

        screenshotStatus.textContent =
            formatOCRStatus(
                progress.status
            );

    }

}


function formatOCRStatus(
    status
) {

    const statusMap = {

        "loading tesseract core":
            "Loading OCR engine...",

        "initializing tesseract":
            "Initializing OCR...",

        "loading language traineddata":
            "Loading language data...",

        "initializing api":
            "Preparing OCR...",

        "recognizing text":
            "Reading screenshot..."

    };


    return (
        statusMap[status] ||
        "Processing screenshot..."
    );

}


/* ============================================================
   OCR RESULT
============================================================ */

function displayOCRResult(
    text
) {

    if (!ocrResultCard) {
        return;
    }


    ocrExtractedText.textContent =
        text;


    ocrResultCard.classList.remove(
        "hidden"
    );

}


function hideOCRResult() {

    if (!ocrResultCard) {
        return;
    }


    ocrResultCard.classList.add(
        "hidden"
    );


    ocrExtractedText.textContent =
        "";

}


/* ============================================================
   BACKEND ANALYSIS
============================================================ */

async function runAnalysis(
    text,
    source = "message"
) {

    /*
        Message analysis starts here with
        isAnalyzing = false.

        Screenshot analysis already set it
        to true before OCR.
    */

    if (
        source === "message" &&
        isAnalyzing
    ) {

        return;

    }


    if (
        source === "message"
    ) {

        isAnalyzing =
            true;

    }


    try {

        hideError();

        hideResult();


        showLoading(
            source === "screenshot"
                ? "Garuda AI is analyzing the extracted text..."
                : "Running the Garuda AI safety pipeline..."
        );


        const response =
            await fetch(
                `${API_URL}/analyze`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message: text
                        })
                }
            );


        if (!response.ok) {

            let serverMessage =
                `Backend returned HTTP ${response.status}.`;


            try {

                const errorData =
                    await response.json();


                if (
                    errorData &&
                    errorData.detail
                ) {

                    serverMessage =
                        errorData.detail;

                }

            } catch (_) {

                // Ignore JSON parsing error.

            }


            throw new Error(
                serverMessage
            );

        }


        const data =
            await response.json();


        hideLoading();


        displayAnalysisResult(
            data
        );


        result.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (err) {

        console.error(
            "Garuda AI analysis error:",
            err
        );


        hideLoading();


        showError(
            getReadableError(
                err,
                "Unable to connect to Garuda AI."
            )
        );

    } finally {

        if (
            source === "message"
        ) {

            isAnalyzing =
                false;

        }

    }

}


/* ============================================================
   DISPLAY ANALYSIS
============================================================ */

function displayAnalysisResult(
    data
) {

    if (!data) {

        showError(
            "Garuda AI returned an empty response."
        );

        return;

    }


    hideError();


    result.classList.remove(
        "hidden"
    );


    const analysis =
        data.analysis ||
        {};


    const risk =
        data.risk ||
        {};


    const explanation =
        data.explanation ||
        {};


    const safety =
        data.safety ||
        {};


    const investigation =
        data.investigation ||
        {};


    const trace =
        data.trace ||
        [];


    const fraudType =
        normalizeFraudType(
            analysis.fraud_type ||
            data.fraud_type ||
            "UNKNOWN"
        );


    const confidence =
        normalizeConfidence(
            analysis.confidence ??
            data.confidence ??
            risk.confidence ??
            0
        );


    const riskScore =
        normalizeRiskScore(
            analysis.risk_score ??
            data.risk_score ??
            risk.risk_score ??
            0
        );


    /*
        IMPORTANT:

        The backend's risk score is preserved.

        We only normalize the DISPLAYED risk label
        when the backend does not provide one.
    */

    const riskLevel =
        normalizeRiskLevel(
            analysis.risk_level ||
            data.risk_level ||
            risk.risk_level ||
            getRiskLevel(
                riskScore
            )
        );


    renderClassification(
        fraudType
    );


    renderRisk(
        riskScore,
        riskLevel
    );


    renderRiskBreakdown(
        fraudType,
        riskScore,
        analysis.signals ||
        data.signals ||
        []
    );


    renderConfidence(
        confidence
    );


    renderSignals(
        analysis.signals ||
        data.signals ||
        []
    );


    renderExplanation(
        explanation,
        data
    );


    renderEvidence(
        explanation,
        investigation
    );


    renderTrace(
        trace
    );


    renderSafety(
        data,
        safety
    );

}


/* ============================================================
   CLASSIFICATION
============================================================ */

function renderClassification(
    fraudType
) {

    fraudTypeElement.textContent =
        prettyFraudType(
            fraudType
        );

}


/* ============================================================
   RISK
============================================================ */

function renderRisk(
    score,
    level
) {

    riskScoreElement.textContent =
        score;


    riskLevelElement.textContent =
        level;


    riskBarFill.style.width =
        `${score}%`;


    const riskColor =
        getRiskColor(
            level
        );


    riskBarFill.style.background =
        riskColor;


    riskLevelElement.style.color =
        riskColor;


    riskScoreElement.style.color =
        riskColor;

}


/* ============================================================
   RISK COLOR
============================================================ */

function getRiskColor(
    level
) {

    switch (
        String(level).toUpperCase()
    ) {

        case "CRITICAL":
            return "#ff557d";

        case "HIGH":
            return "#ff8f56";

        case "MODERATE":
            return "#ffc857";

        case "SUSPICIOUS":
            /*
                Backward compatibility in case an
                older backend still returns SUSPICIOUS.
            */
            return "#ffc857";

        case "LOW":
        default:
            return "#42d99a";

    }

}


/* ============================================================
   RISK BREAKDOWN
============================================================ */

function renderRiskBreakdown(
    fraudType,
    riskScore,
    signals
) {

    /*
        Optional UI.

        If index.html does not contain
        #risk-breakdown, nothing happens.

        This means the rest of the frontend
        remains fully compatible.
    */

    if (!riskBreakdownElement) {
        return;
    }


    riskBreakdownElement.innerHTML =
        "";


    const baseScores = {

        BANK_IMPERSONATION: 20,
        OTP_SCAM: 35,
        UPI_FRAUD: 30,
        KYC_SCAM: 25,
        JOB_SCAM: 25,
        INVESTMENT_SCAM: 30,
        COURIER_SCAM: 25,
        DIGITAL_ARREST: 40,
        GOVERNMENT_IMPERSONATION: 25,
        FAKE_CUSTOMER_SUPPORT: 25,
        ROMANCE_SCAM: 25,
        LOTTERY_SCAM: 25,
        PHISHING: 25,
        MALWARE: 35,
        SIM_SWAP: 40,
        LOAN_SCAM: 25,
        CHARITY_SCAM: 20,
        OTHER: 10,
        NOT_FRAUD: 0

    };


    const signalScores = {

        impersonation: 20,
        urgency: 15,
        threat: 20,
        otp_request: 40,
        credential_request: 35,
        password_request: 40,
        pin_request: 40,
        personal_information_request: 25,
        payment_request: 30,
        upi_request: 30,
        qr_payment: 30,
        suspicious_link: 25,
        remote_access_request: 40,
        job_offer: 10,
        investment_offer: 15,
        unrealistic_return: 30,
        kyc_request: 20,
        account_verification: 15,
        prize_claim: 15,
        legal_threat: 20,
        emotional_pressure: 15

    };


    const base =
        baseScores[fraudType] || 0;


    let contributions = [];


    if (base > 0) {

        contributions.push({
            label:
                `${prettyFraudType(fraudType)} base risk`,
            value:
                base
        });

    }


    if (Array.isArray(signals)) {

        signals.forEach(
            signal => {

                const normalized =
                    String(signal)
                        .toLowerCase()
                        .trim();


                const value =
                    signalScores[normalized];


                if (
                    typeof value === "number"
                ) {

                    contributions.push({
                        label:
                            prettySignal(signal),
                        value:
                            value
                    });

                }

            }
        );

    }


    /*
        The real backend score is authoritative.

        We calculate a DISPLAY contribution total
        only for explanation purposes.

        We never overwrite the backend score.
    */

    const total =
        contributions.reduce(
            (sum, item) =>
                sum + item.value,
            0
        );


    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "risk-breakdown-content";


    contributions.forEach(
        item => {

            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "risk-breakdown-row";


            const label =
                document.createElement(
                    "span"
                );

            label.textContent =
                item.label;


            const value =
                document.createElement(
                    "strong"
                );

            value.textContent =
                `+${item.value}`;


            row.appendChild(
                label
            );

            row.appendChild(
                value
            );

            wrapper.appendChild(
                row
            );

        }
    );


    const separator =
        document.createElement(
            "div"
        );

    separator.className =
        "risk-breakdown-separator";


    wrapper.appendChild(
        separator
    );


    const finalRow =
        document.createElement(
            "div"
        );

    finalRow.className =
        "risk-breakdown-row risk-breakdown-total";


    const finalLabel =
        document.createElement(
            "span"
        );

    finalLabel.textContent =
        "Final Risk Score";


    const finalValue =
        document.createElement(
            "strong"
        );

    finalValue.textContent =
        `${riskScore}/100`;


    finalRow.appendChild(
        finalLabel
    );

    finalRow.appendChild(
        finalValue
    );


    wrapper.appendChild(
        finalRow
    );


    /*
        If the displayed contribution total does not
        equal the backend score, make that explicit
        instead of pretending the frontend calculation
        is the actual backend calculation.
    */

    if (
        total !== riskScore
    ) {

        const note =
            document.createElement(
                "small"
            );

        note.className =
            "risk-breakdown-note";

        note.textContent =
            "Score calculated by Garuda AI Risk Engine.";

        wrapper.appendChild(
            note
        );

    }


    riskBreakdownElement.appendChild(
        wrapper
    );

}


/* ============================================================
   CONFIDENCE
============================================================ */

function renderConfidence(
    confidence
) {

    const percentage =
        Math.round(
            confidence * 100
        );


    confidenceElement.textContent =
        `${percentage}%`;


    confidenceBarFill.style.width =
        `${percentage}%`;


    if (
        percentage >= 80
    ) {

        confidenceBarFill.style.background =
            "#42d99a";

    } else if (
        percentage >= 60
    ) {

        confidenceBarFill.style.background =
            "#ffc857";

    } else {

        confidenceBarFill.style.background =
            "#ff557d";

    }

}


/* ============================================================
   SIGNALS
============================================================ */

function renderSignals(
    signals
) {

    signalsElement.innerHTML =
        "";


    if (
        !Array.isArray(signals) ||
        signals.length === 0
    ) {

        signalsElement.innerHTML =
            `<span class="no-data">No specific signals returned.</span>`;

        return;

    }


    signals.forEach(
        signal => {

            const chip =
                document.createElement(
                    "span"
                );


            chip.className =
                "signal-chip";


            chip.textContent =
                prettySignal(
                    signal
                );


            signalsElement.appendChild(
                chip
            );

        }
    );

}


/* ============================================================
   EXPLANATION
============================================================ */

function renderExplanation(
    explanation,
    data
) {

    const fraudType =
        normalizeFraudType(
            data.analysis?.fraud_type ||
            data.fraud_type ||
            "OTHER"
        );


    let attackerGoal =
        explanation.attacker_goal ||
        explanation.attackerGoal ||
        data.attacker_goal ||
        "";


    /*
        Fraud-type-specific fallback goals.

        This protects the UI from an incorrect or
        unhelpful model-generated sentence.
    */

    const fallbackGoals = {

        BANK_IMPERSONATION:
            "To impersonate a trusted bank or organization and obtain sensitive information such as an OTP.",

        OTP_SCAM:
            "To obtain your OTP or authentication code and potentially gain unauthorized access.",

        UPI_FRAUD:
            "To trick you into making a UPI payment or approving a fraudulent transaction.",

        KYC_SCAM:
            "To obtain sensitive personal or banking information by pretending that KYC verification is required.",

        JOB_SCAM:
            "To obtain money or sensitive information by pretending to offer a job.",

        INVESTMENT_SCAM:
            "To obtain money through a fraudulent investment opportunity or unrealistic return promise.",

        COURIER_SCAM:
            "To obtain money or sensitive information by pretending that a parcel requires payment or verification.",

        DIGITAL_ARREST:
            "To intimidate you with a fake legal or police threat and obtain money or sensitive information.",

        GOVERNMENT_IMPERSONATION:
            "To impersonate a government authority and obtain money or sensitive information.",

        FAKE_CUSTOMER_SUPPORT:
            "To impersonate customer support and obtain credentials, payment information, or remote access.",

        PHISHING:
            "To trick you into revealing credentials or sensitive information through a fraudulent message or link.",

        MALWARE:
            "To trick you into installing malicious software that may access sensitive information on your device.",

        LOTTERY_SCAM:
            "To obtain money or sensitive information by pretending that you have won a prize.",

        ROMANCE_SCAM:
            "To build trust and eventually obtain money or sensitive information.",

        SIM_SWAP:
            "To take control of your mobile number and potentially access accounts protected by SMS verification.",

        LOAN_SCAM:
            "To obtain money or sensitive information by pretending to offer a loan.",

        CHARITY_SCAM:
            "To obtain money by pretending to represent a legitimate charitable cause."

    };


    /*
        Detect known bad fallback text.
    */

    const normalizedGoal =
        String(
            attackerGoal
        )
            .trim()
            .toLowerCase();


    if (
        !attackerGoal ||
        normalizedGoal === "n/a" ||
        normalizedGoal.includes(
            "prevent phishing"
        ) ||
        normalizedGoal.includes(
            "prevent fraud"
        ) ||
        normalizedGoal === "to prevent phishing attempts"
    ) {

        attackerGoal =
            fallbackGoals[fraudType] ||
            "To obtain money, sensitive information, credentials, or unauthorized access.";

    }


    const recommendedAction =
        explanation.recommended_action ||
        explanation.recommendedAction ||
        data.recommended_action ||
        "Do not share OTPs, passwords, PINs, or sensitive information. Verify the request using an official channel.";


    attackerGoalElement.textContent =
        attackerGoal;


    recommendedActionElement.textContent =
        recommendedAction;

}


/* ============================================================
   EVIDENCE
============================================================ */

function renderEvidence(
    explanation,
    investigation
) {

    evidenceList.innerHTML =
        "";


    let evidence =
        explanation.rag_evidence ||
        explanation.ragEvidence ||
        [];


    if (
        !Array.isArray(evidence) ||
        evidence.length === 0
    ) {

        evidence =
            investigation.results ||
            [];

    }


    if (
        !Array.isArray(evidence) ||
        evidence.length === 0
    ) {

        evidenceList.innerHTML =
            `<div class="no-data">No grounding evidence was returned.</div>`;

        return;

    }


    evidence.forEach(
        item => {

            const element =
                document.createElement(
                    "div"
                );


            element.className =
                "evidence-item";


            const title =
                item.title ||
                "Trusted evidence";


            const fraudType =
                item.fraud_type ||
                item.fraudType ||
                "";


            const text =
                item.evidence ||
                item.text ||
                item.content ||
                "No evidence description available.";


            const source =
                item.source ||
                "Trusted source";


            const sourceUrl =
                item.source_url ||
                item.sourceUrl ||
                "";


            const distance =
                item.relevance_distance;


            const top =
                document.createElement(
                    "div"
                );


            top.className =
                "evidence-top";


            const titleElement =
                document.createElement(
                    "span"
                );


            titleElement.className =
                "evidence-title";


            titleElement.textContent =
                title;


            top.appendChild(
                titleElement
            );


            if (fraudType) {

                const typeElement =
                    document.createElement(
                        "span"
                    );


                typeElement.className =
                    "evidence-type";


                typeElement.textContent =
                    prettyFraudType(
                        fraudType
                    );


                top.appendChild(
                    typeElement
                );

            }


            const textElement =
                document.createElement(
                    "p"
                );


            textElement.className =
                "evidence-text";


            textElement.textContent =
                text;


            const sourceElement =
                document.createElement(
                    "div"
                );


            sourceElement.className =
                "evidence-source";


            const sourceText =
                document.createElement(
                    "span"
                );


            sourceText.textContent =
                source;


            sourceElement.appendChild(
                sourceText
            );


            if (sourceUrl) {

                const link =
                    document.createElement(
                        "a"
                    );


                link.href =
                    sourceUrl;


                link.target =
                    "_blank";


                link.rel =
                    "noopener noreferrer";


                link.textContent =
                    "View source";


                sourceElement.appendChild(
                    link
                );

            }


            if (
                typeof distance ===
                "number"
            ) {

                const distanceText =
                    document.createElement(
                        "span"
                    );


                distanceText.textContent =
                    `Distance: ${distance.toFixed(3)}`;


                sourceElement.appendChild(
                    distanceText
                );

            }


            element.appendChild(
                top
            );


            element.appendChild(
                textElement
            );


            element.appendChild(
                sourceElement
            );


            evidenceList.appendChild(
                element
            );

        }
    );

}


/* ============================================================
   TRACE
============================================================ */

function renderTrace(
    trace
) {

    traceList.innerHTML =
        "";


    if (
        !Array.isArray(trace) ||
        trace.length === 0
    ) {

        traceList.innerHTML =
            `<div class="no-data">No trace information returned.</div>`;

        return;

    }


    trace.forEach(
        entry => {

            const element =
                document.createElement(
                    "div"
                );


            element.className =
                "trace-item";


            const component =
                document.createElement(
                    "span"
                );


            component.className =
                "trace-component";


            component.textContent =
                entry.component ||
                "Garuda AI";


            const event =
                document.createElement(
                    "span"
                );


            event.className =
                "trace-event";


            event.textContent =
                entry.event ||
                "EVENT";


            const duration =
                document.createElement(
                    "span"
                );


            duration.className =
                "trace-duration";


            if (
                typeof entry.duration_ms ===
                "number"
            ) {

                duration.textContent =
                    `${entry.duration_ms.toFixed(2)} ms`;

            } else {

                duration.textContent =
                    "—";

            }


            element.appendChild(
                component
            );


            element.appendChild(
                event
            );


            element.appendChild(
                duration
            );


            if (entry.reason) {

                const reason =
                    document.createElement(
                        "span"
                    );


                reason.className =
                    "trace-reason";


                reason.textContent =
                    `Reason: ${entry.reason}`;


                element.appendChild(
                    reason
                );

            }


            traceList.appendChild(
                element
            );

        }
    );

}


/* ============================================================
   SAFETY
============================================================ */

function renderSafety(
    data,
    safety
) {

    const status =
        String(
            data.status ||
            ""
        ).toUpperCase();


    const decision =
        String(
            safety.decision ||
            data.decision ||
            ""
        ).toUpperCase();


    const shouldEscalate =
        status === "ESCALATED" ||
        decision === "ESCALATE";


    if (!shouldEscalate) {

        escalationCard.classList.add(
            "hidden"
        );


        resultStatusBadge.textContent =
            "✓ Safety checks passed";


        resultStatusBadge.style.color =
            "#79e4b4";


        return;

    }


    escalationCard.classList.remove(
        "hidden"
    );


    resultStatusBadge.textContent =
        "⚠ Human verification required";


    resultStatusBadge.style.color =
        "#ffc857";


    const reasons =
        data.escalation_reasons ||
        safety.reasons ||
        [];


    escalationReasons.innerHTML =
        "";


    if (
        !Array.isArray(reasons) ||
        reasons.length === 0
    ) {

        const reason =
            document.createElement(
                "span"
            );


        reason.className =
            "escalation-reason";


        reason.textContent =
            "Safety escalation";


        escalationReasons.appendChild(
            reason
        );


        return;

    }


    reasons.forEach(
        item => {

            const reason =
                document.createElement(
                    "span"
                );


            reason.className =
                "escalation-reason";


            reason.textContent =
                prettyReason(
                    item
                );


            escalationReasons.appendChild(
                reason
            );

        }
    );

}


/* ============================================================
   LOADING
============================================================ */

function showLoading(
    text
) {

    if (!loading) {
        return;
    }


    loading.classList.remove(
        "hidden"
    );


    if (loadingMessage) {

        loadingMessage.textContent =
            text ||
            "Running the safety pipeline...";

    }


    updatePipeline(
        text
    );

}


function hideLoading() {

    if (loading) {

        loading.classList.add(
            "hidden"
        );

    }

}


/* ============================================================
   PIPELINE
============================================================ */

function updatePipeline(
    text
) {

    const items =
        document.querySelectorAll(
            ".pipeline-item"
        );


    if (!items.length) {
        return;
    }


    const lower =
        String(
            text || ""
        ).toLowerCase();


    let activeIndex =
        0;


    if (
        lower.includes("ocr") ||
        lower.includes("screenshot") ||
        lower.includes("reading")
    ) {

        activeIndex =
            0;

    } else if (
        lower.includes("fraud") ||
        lower.includes("analysis")
    ) {

        activeIndex =
            1;

    } else if (
        lower.includes("risk")
    ) {

        activeIndex =
            2;

    } else if (
        lower.includes("mcp") ||
        lower.includes("rag") ||
        lower.includes("investigat")
    ) {

        activeIndex =
            3;

    } else if (
        lower.includes("safety")
    ) {

        activeIndex =
            4;

    }


    items.forEach(
        (item, index) => {

            item.classList.toggle(
                "active",
                index === activeIndex
            );

        }
    );

}


/* ============================================================
   ERROR
============================================================ */

function setupErrorHandling() {

    if (errorDismiss) {

        errorDismiss.addEventListener(
            "click",
            hideError
        );

    }

}


function showError(
    messageText
) {

    hideLoading();


    if (!error) {
        return;
    }


    error.classList.remove(
        "hidden"
    );


    errorMessage.textContent =
        messageText;


    error.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


function hideError() {

    if (error) {

        error.classList.add(
            "hidden"
        );

    }

}


/* ============================================================
   RESET
============================================================ */

function setupResetButton() {

    if (!newScanButton) {
        return;
    }


    newScanButton.addEventListener(
        "click",
        resetApplication
    );

}


function resetApplication() {

    hideResult();

    hideError();

    hideLoading();

    hideOCRResult();


    if (message) {

        message.value =
            "";

    }


    updateCharacterCount();


    removeScreenshot();


    switchMode(
        "message"
    );


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


function hideResult() {

    if (result) {

        result.classList.add(
            "hidden"
        );

    }


    if (escalationCard) {

        escalationCard.classList.add(
            "hidden"
        );

    }

}


/* ============================================================
   SCREENSHOT CONTROL
============================================================ */

function setScreenshotControlsDisabled(
    disabled
) {

    if (removeImageButton) {

        removeImageButton.disabled =
            disabled;

    }


    if (analyzeScreenshotButton) {

        analyzeScreenshotButton.disabled =
            disabled ||
            !selectedScreenshot;

    }


    if (ocrLanguage) {

        ocrLanguage.disabled =
            disabled;

    }

}


/* ============================================================
   NORMALIZATION
============================================================ */

function normalizeConfidence(
    value
) {

    let number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return 0;

    }


    if (number > 1) {

        number =
            number / 100;

    }


    return Math.max(
        0,
        Math.min(
            1,
            number
        )
    );

}


function normalizeRiskScore(
    value
) {

    const number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return 0;

    }


    return Math.max(
        0,
        Math.min(
            100,
            Math.round(number)
        )
    );

}


function normalizeRiskLevel(
    value
) {

    const normalized =
        String(
            value ||
            ""
        ).toUpperCase();


    /*
        Convert the old backend/frontend label
        into the new presentation label.
    */

    if (
        normalized ===
        "SUSPICIOUS"
    ) {

        return "MODERATE";

    }


    return normalized ||
        "LOW";

}


function normalizeFraudType(
    value
) {

    return String(
        value ||
        "UNKNOWN"
    ).toUpperCase();

}


/*
    Risk bands used by Garuda AI UI:

    0–24     LOW
    25–49    MODERATE
    50–74    HIGH
    75–100   CRITICAL
*/

function getRiskLevel(
    score
) {

    if (score <= 24) {

        return "LOW";

    }


    if (score <= 49) {

        return "MODERATE";

    }


    if (score <= 74) {

        return "HIGH";

    }


    return "CRITICAL";

}


/* ============================================================
   PRETTY DISPLAY
============================================================ */

function prettyFraudType(
    value
) {

    if (!value) {

        return "Unknown";

    }


    return String(value)
        .replace(
            /_/g,
            " "
        )
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );

}


function prettySignal(
    value
) {

    if (!value) {

        return "Unknown signal";

    }


    return String(value)
        .replace(
            /_/g,
            " "
        )
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );

}


function prettyReason(
    value
) {

    if (!value) {

        return "Safety check";

    }


    return String(value)
        .replace(
            /_/g,
            " "
        )
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );

}


/* ============================================================
   ERROR MESSAGE
============================================================ */

function getReadableError(
    errorObject,
    fallback
) {

    if (!errorObject) {

        return fallback;

    }


    const message =
        errorObject.message;


    if (!message) {

        return fallback;

    }


    if (
        message.includes(
            "Failed to fetch"
        )
    ) {

        return (
            "Garuda AI backend is not reachable. " +
            "Make sure the FastAPI server is running on " +
            "http://127.0.0.1:8000."
        );

    }


    return message;

}


/* ============================================================
   CLEANUP
============================================================ */

window.addEventListener(
    "beforeunload",
    () => {

        if (
            selectedScreenshotUrl
        ) {

            URL.revokeObjectURL(
                selectedScreenshotUrl
            );

        }

    }
);


/* ============================================================
   FINAL DEBUG
============================================================ */

console.log(
    "Garuda AI frontend loaded."
);

console.log(
    "API:",
    API_URL
);

console.log(
    "Tesseract:",
    typeof Tesseract !== "undefined"
);