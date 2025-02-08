let mediaRecorder;
let audioChunks = [];
let isRecording = false;

document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const recordButtonText = document.getElementById('recordButtonText');
    const recordingStatus = document.getElementById('recordingStatus');
    const clearButton = document.getElementById('clearButton');
    const conversationLog = document.getElementById('conversationLog');

    async function setupRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                await sendAudioToServer(audioBlob);
                audioChunks = [];
            };
        } catch (error) {
            console.error('Error accessing microphone:', error);
            recordingStatus.textContent = 'Error: Could not access microphone';
        }
    }

    async function sendAudioToServer(audioBlob) {
        try {
            recordingStatus.textContent = 'Processing...';

            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.mp3');

            const response = await fetch('/voice-assistant/audio-message', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle the audio response
            const audioResponse = await response.blob();
            const audioUrl = URL.createObjectURL(audioResponse);

            // Add messages to conversation log
            addMessageToLog('You', 'Audio message sent', 'user-message');

            // Play the response
            const audio = new Audio(audioUrl);
            audio.play();

            recordingStatus.textContent = 'Response received and playing';
        } catch (error) {
            console.error('Error sending audio:', error);
            recordingStatus.textContent = 'Error processing audio';
        }
    }

    function addMessageToLog(sender, message, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        conversationLog.appendChild(messageDiv);
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }

    recordButton.addEventListener('click', () => {
        if (!isRecording) {
            // Start recording
            mediaRecorder.start();
            isRecording = true;
            recordButton.classList.add('recording');
            recordButton.classList.remove('bg-blue-500');
            recordButton.classList.add('bg-red-500');
            recordButtonText.textContent = 'Stop Recording';
            recordingStatus.textContent = 'Recording...';
        } else {
            // Stop recording
            mediaRecorder.stop();
            isRecording = false;
            recordButton.classList.remove('recording');
            recordButton.classList.remove('bg-red-500');
            recordButton.classList.add('bg-blue-500');
            recordButtonText.textContent = 'Start Recording';
            recordingStatus.textContent = 'Processing audio...';
        }
    });

    clearButton.addEventListener('click', () => {
        conversationLog.innerHTML = '';
        recordingStatus.textContent = 'Conversation history cleared';
    });

    // Initialize recording setup
    setupRecording();
});