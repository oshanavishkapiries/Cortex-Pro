ප්ලගින (Plugins/Extensions) මගින් සිදු කරන්නේ තෙවන පාර්ශවීය වෙබ් අඩවිවලින් (උදා: YouTube, Twitch හෝ වෙනත් චිත්‍රපට අඩවි) දත්ත ලබාගෙන එය Cloudstream යෙදුමට තේරුම් ගත හැකි පොදු ආකෘතියකට (JSON වැනි) හැරවීමයි. 

ප්‍රධාන වශයෙන් ප්ලගිනයක් අදියර 3ක් යටතේ ක්‍රියා කරයි:
1. **Search (සෙවීම):** පරිශීලකයා නමක් සෙවූ විට, ප්ලගිනය එම වෙබ් අඩවියේ සොයා ප්‍රතිඵල ලබා දෙයි.
2. **Load (තොරතුරු ලබා ගැනීම):** චිත්‍රපටයක් හෝ කතාමාලාවක් තේරූ විට, එහි කොටස් (episodes), පෝස්ටරය සහ විස්තර ලබා ගනී.
3. **Extract (වීඩියෝ සබැඳිය ලබා ගැනීම):** ධාවනය කිරීමට තේරූ විට, අදාළ වෙබ් අඩවියේ ඇති සෘජු වීඩියෝ සබැඳිය (.mp4 හෝ .m3u8) ලබා ගනී.

ප්ලගිනයකින් යෙදුමට ලබා දෙන ප්‍රතිදානයක (Output) ආදර්ශයක් (JSON ආකාරයෙන්):

```json
{
  "name": "The Open Source Movie",
  "url": "https://example.com/movie/123",
  "posterUrl": "https://example.com/images/poster.jpg",
  "year": 2023,
  "plot": "මෙය චිත්‍රපටයේ කෙටි විස්තරයකි...",
  "episodes": [
    {
      "name": "Full Movie",
      "data": "https://example.com/watch/123",
      "season": 1,
      "episode": 1
    }
  ]
}
```

ඉන්පසු පරිශීලකයා වීඩියෝව Play කළ විට, ප්ලගිනය මගින් ධාවකයට (ExoPlayer) ලබා දෙන සෘජු වීඩියෝ සබැඳියේ ආකෘතිය (ExtractorLink):

```json
{
  "name": "Server 1 - 1080p",
  "url": "https://video-server.com/streams/movie123_1080p.m3u8",
  "referer": "https://example.com/",
  "quality": 1080,
  "isM3u8": true
}
```

මෙම සෘජු `url` එක භාවිතා කර Cloudstream යෙදුම ExoPlayer හරහා වීඩියෝව ඔබට පෙන්වයි.
