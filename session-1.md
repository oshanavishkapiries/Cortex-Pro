ඔබ ලබා දුන් `extensions` ෆෝල්ඩරය පරීක්ෂා කිරීමේදී, එය Cloudstream Extension Repository එකක් බව තහවුරු විය. එහි **Dailymotion, InternetArchive, Invidious, Twitch, සහ Youtube** වැනි ප්‍රයෝජනවත් (valuable) ප්ලගින කිහිපයක් අඩංගු වේ.

අප එහි ඇති `DailymotionProvider.kt` ගොනුව අධ්‍යයනය කළෙමු. එය Cloudstream ප්ලගිනයක සම්පූර්ණ ජීවන චක්‍රය මනාව පෙන්වයි.

**Dailymotion ප්ලගිනයේ ක්‍රියාවලිය:**
1. **මුල් පිටුව (Main Page):** Dailymotion පොදු API එක (`https://api.dailymotion.com/videos`) වෙත ඉල්ලීමක් යවා ජනප්‍රිය වීඩියෝ ලැයිස්තුවක් ලබා ගනී.
2. **සෙවීම (Search):** පරිශීලකයා සෙවූ විට, එම API එක හරහාම අදාළ නමට ගැලපෙන වීඩියෝවල ID සහ පෝස්ටර් ලබා දෙයි.
3. **විස්තර ලබා ගැනීම (Load):** තෝරාගත් වීඩියෝවේ ID එක යොදාගෙන එහි සම්පූර්ණ විස්තර (Description ආදිය) ලබා ගනී.
4. **වීඩියෝව ධාවනය (Extract):** `https://www.dailymotion.com/embed/video/{id}` හරහා Cloudstream හි ඇති අභ්‍යන්තර Dailymotion Extractor එකට සබැඳිය යොමු කර සෘජු වීඩියෝ සබැඳිය උකහා ගනී.

**මෙම ක්‍රියාවලිය JavaScript මගින් නැවත නිර්මාණය කිරීමේ ආකෘතියක් (Live Output Check):**

ඔබට මෙය Node.js හරහා ක්‍රියාත්මක කර බැලිය හැක:

```javascript
const axios = require('axios');

const MAIN_URL = "https://api.dailymotion.com";

// 1. Search කිරීම
async function searchDailymotion(query) {
    const url = `${MAIN_URL}/videos?fields=id,title,thumbnail_360_url&limit=5&search=${encodeURIComponent(query)}`;
    const response = await axios.get(url);
    
    console.log("--- Search Results ---");
    response.data.list.forEach(video => {
        console.log(`Title: ${video.title}\nID: ${video.id}\nLink: https://www.dailymotion.com/video/${video.id}\n`);
    });
    
    return response.data.list;
}

// 2. Load කිරීම (විස්තර ලබාගැනීම)
async function loadVideo(videoId) {
    const url = `${MAIN_URL}/video/${videoId}?fields=id,title,description,thumbnail_720_url`;
    const response = await axios.get(url);
    
    console.log("--- Video Details ---");
    console.log(`Title: ${response.data.title}`);
    console.log(`Description: ${response.data.description.substring(0, 100)}...`);
}

// ක්‍රියාත්මක කර පරීක්ෂා කිරීම
(async () => {
    // "Spider-man" ලෙස සෙවීම
    const results = await searchDailymotion("Spider-man");
    if(results.length > 0) {
        // පළමු ප්‍රතිඵලයේ විස්තර ලබා ගැනීම
        await loadVideo(results[0].id);
        console.log("\n[Extraction] ධාවනය කිරීම සඳහා Dailymotion Extractor වෙත යැවිය යුතු සබැඳිය:");
        console.log(`https://www.dailymotion.com/embed/video/${results[0].id}`);
    }
})();
```

මෙයින් ප්ලගිනයක් විසින් යෙදුමට ලබා දෙන දත්ත (Outputs) ඔබට සජීවීව පරීක්ෂා කළ හැක.
