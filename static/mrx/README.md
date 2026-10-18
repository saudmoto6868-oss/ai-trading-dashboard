# Mr X - the real presenter (files go here)

The guide uses these files instead of the drawn presenter as soon as they exist (Streamlit static serving,
`.streamlit/config.toml` -> `enableStaticServing = true`, URL `/app/static/mrx/...`).

## Free option (recommended now): photo + mouth frames
Same man, same framing, same size (portrait 9:16, e.g. 720x1280 JPG). Only the mouth / eyes change:

| file | what |
|---|---|
| `photo.jpg` | mouth closed, eyes open (the base picture) |
| `mid.jpg` | mouth slightly open |
| `open.jpg` | mouth open as when saying "aa" |
| `blink.jpg` | eyes closed, mouth closed |

During a live call (Gemini Live) the mouth frame follows his real voice level; blinking every few seconds; slow breathing motion.
Make them free with Gemini (image editing keeps the same face): create `photo.jpg` first, then ask Gemini to edit that same
picture: "keep everything identical, only open the mouth slightly" -> `mid.jpg`, "... open the mouth as if saying aa" -> `open.jpg`,
"... only close the eyes" -> `blink.jpg`.

## Video option
| file | what | spec |
|---|---|---|
| `idle.mp4` | standing, small natural movement, mouth closed | portrait 9:16 (720x1280), H.264 MP4, 5-10 s seamless loop, no sound, < 5 MB |
| `talk.mp4` | the same man talking with light hand gestures | same spec, same framing as idle |

Dark studio background, head to knees, centred, soft key light. The edges fade out on the stage.
Only use a person you have the rights to (an AI-generated person / yourself / someone who signed a consent / a licensed avatar),
never a real person's photo taken from the internet.
