import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const openaiKey = process.env.OPENAI_API_KEY;
    const deepgramToken = process.env.DEEPGRAM_API_TOKEN;

    if (!openaiKey && !deepgramToken) {
      console.error("No transcription API keys configured");
      return NextResponse.json(
        { error: "No transcription API keys configured" },
        { status: 500 }
      );
    }

    const audioData = await request.arrayBuffer();

    if (!audioData || audioData.byteLength === 0) {
      console.error("No audio data received");
      return NextResponse.json(
        { error: "No audio data received" },
        { status: 400 }
      );
    }

    const contentType = request.headers.get("content-type") || "audio/webm";
    console.log(
      `Transcription request: ${audioData.byteLength} bytes, type: ${contentType}`
    );

    // Primary: Use OpenAI Whisper API
    if (openaiKey) {
      try {
        const transcript = await transcribeWithOpenAI(
          openaiKey,
          audioData,
          contentType
        );
        if (transcript && transcript.trim()) {
          console.log(`OpenAI Whisper transcript: "${transcript}"`);
          // Return in Deepgram-compatible format so client code works unchanged
          return NextResponse.json({
            results: {
              channels: [
                {
                  alternatives: [{ transcript }],
                },
              ],
            },
          });
        }
        console.warn("OpenAI Whisper returned empty transcript, trying Deepgram fallback");
      } catch (openaiError) {
        console.error("OpenAI Whisper error:", openaiError.message);
        if (!deepgramToken) {
          return NextResponse.json(
            { error: `Transcription failed: ${openaiError.message}` },
            { status: 500 }
          );
        }
        console.log("Falling back to Deepgram...");
      }
    }

    // Fallback: Use Deepgram
    if (deepgramToken) {
      try {
        const data = await transcribeWithDeepgram(
          deepgramToken,
          audioData,
          contentType
        );
        const transcript =
          data?.results?.channels?.[0]?.alternatives?.[0]?.transcript || "";
        console.log(`Deepgram transcript: "${transcript}"`);
        return NextResponse.json(data);
      } catch (deepgramError) {
        console.error("Deepgram error:", deepgramError.message);
        return NextResponse.json(
          { error: `Transcription failed: ${deepgramError.message}` },
          { status: 500 }
        );
      }
    }

    return NextResponse.json(
      { error: "All transcription methods failed" },
      { status: 500 }
    );
  } catch (error) {
    console.error("Transcription proxy error:", error);
    return NextResponse.json(
      { error: "Transcription failed" },
      { status: 500 }
    );
  }
}

async function transcribeWithOpenAI(apiKey, audioBuffer, contentType) {
  const extMap = {
    "audio/webm": "webm",
    "audio/webm;codecs=opus": "webm",
    "audio/ogg": "ogg",
    "audio/ogg;codecs=opus": "ogg",
    "audio/mp4": "mp4",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/flac": "flac",
  };

  const baseType = contentType.split(";")[0].trim().toLowerCase();
  const ext = extMap[baseType] || "webm";

  const blob = new Blob([audioBuffer], { type: contentType });
  const formData = new FormData();
  formData.append("file", blob, `recording.${ext}`);
  formData.append("model", "whisper-1");
  formData.append("language", "en");

  const response = await fetch(
    "https://api.openai.com/v1/audio/transcriptions",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      body: formData,
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${errorText}`);
  }

  const data = await response.json();
  return data.text || "";
}

async function transcribeWithDeepgram(apiToken, audioBuffer, contentType) {
  const response = await fetch(
    "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&numerals=true",
    {
      method: "POST",
      headers: {
        Authorization: `Token ${apiToken}`,
        "Content-Type": contentType,
      },
      body: audioBuffer,
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Deepgram API error ${response.status}: ${errorText}`);
  }

  return await response.json();
}
