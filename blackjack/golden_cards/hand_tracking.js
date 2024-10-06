// Define variables for MediaPipe Hands model and video
let hands;
let video;
let canvas;
let context;

// Function to set up camera and start hand detection
async function setupCamera() {
    video = document.getElementById('video');

    // Get user media (access webcam)
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream; // Set video source to webcam stream

    // Load MediaPipe Hands model
    hands = new Hands({ locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    } });
    await hands.initialize();
    await hands.start();

    // Create canvas for drawing landmarks
    canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context = canvas.getContext('2d');
    document.body.appendChild(canvas);
}


// Function to detect hands in video frames
async function detectHands() {
    // Wait for the video to be loaded
    if (video.readyState !== 4) {
        setTimeout(detectHands, 100);
        return;
    }

    // Estimate hands from video element
    const results = await hands.send({ image: video });

    // Draw video frame and landmarks
    drawLandmarks(results);

    // Continue to detect hands recursively
    requestAnimationFrame(detectHands);
}

// Function to draw video frame and landmarks
function drawLandmarks(results) {
    // Clear canvas
    context.clearRect(0, 0, canvas.width, canvas.height);

    // Draw video frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Draw landmarks on detected hands
    if (results.multiHandLandmarks) {
        results.multiHandLandmarks.forEach(hand => {
            hand.forEach((landmark, index) => {
                const x = landmark.x * canvas.width;
                const y = landmark.y * canvas.height;
                context.fillStyle = 'red';
                context.beginPath();
                context.arc(x, y, 5, 0, 2 * Math.PI);
                context.fill();
            });
        });
    }
}

// Start the camera and hand detection
setupCamera().then(detectHands);
