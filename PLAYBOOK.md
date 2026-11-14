# Techu Machi: nightly post playbook

Instagram: **@techumachi**, a tech news and tips page for an Indian (Chennai/Tamil Nadu) audience.
Every night, make the NEXT day's two carousel posts plus a Reel of the news post, upload the files, and schedule all three in Metricool.

## Fixed settings

| Item | Value |
|---|---|
| Metricool brand id (blogId) | `7591592` (timezone Asia/Calcutta) |
| Network | instagram, type POST (carousel), autoPublish true, isAiGenerated false |
| Repo / branch | `techumachiofficial-blip/SUVs-projects`, branch `posts` |
| Image folder | `YYYY-MM-DD/` (the date the post goes live) |
| Image URL format | `https://raw.githubusercontent.com/techumachiofficial-blip/SUVs-projects/posts/YYYY-MM-DD/<file>.jpg` |
| Design toolkit | `tools/techumachi.py` (fonts in `tools/fonts/`, logo is `logo.png`) |
| Reel maker | `tools/reel.py OUT.mp4 slide1.jpg slide2.jpg ...` turns the news carousel into a 1080x1920 MP4 (silent audio track) plus `<name>_cover.jpg` |
| History log | `HISTORY.md`: read it first so topics are never repeated; append each night |

## Posting slots (IST)

- **1:00 PM: useful post** (evergreen, gets saved). Theme by weekday:
  - Mon: AI tool of the week
  - Tue: phone settings tip
  - Wed: useful app
  - Thu: online safety (UPI/OTP scams, privacy)
  - Fri: phone buying guide (best under a ₹ budget)
  - Sat: tech myths vs facts
  - Sun: the week's top 5 tech news recap
- **7:00 PM: trending tech news** (the biggest India-relevant tech story of the last 24-48 hours: launches, prices, telecom, AI).
- **9:00 PM: Reel of the 7 PM news post** (same slides as a video, to reach non-followers). If the 7 PM slot became an evergreen post, make the Reel from that one instead.

## Content rules (owner's standing instructions)

1. **Full English** on slides and captions.
2. **Exactly 5 hashtags** per post (Instagram caps posts at 5), using big, popular relevant tags, e.g. #technology #tech #smartphone #techtips #android #iphone, plus 1-2 topic tags such as #oppo or #ai.
3. **Techu Machi logo watermark on every slide.** `frame()` adds it automatically.
4. Mention the official brand handle in news captions (e.g. @apple, @oppoindia, @samsungindia, @flipkart, @amazondotin).
5. Carousels of 3-6 slides, 1080x1350. Slide 1 is a strong hook, the middle slides carry the facts, and the last slide asks a comment question.
6. Caption: hook line, short facts with emoji bullets, a call to comment or save, "Follow @techumachi for daily tech news ⚡", then the 5 hashtags.

## Accuracy and copyright (must follow)

- Every news fact (price, date, spec) must come from a reputable source found via web search **that day** (e.g. GSMArena, Smartprix, 91mobiles, Business Today, Gadgets360). Cross-check prices in 2 sources. Label rumours "expected" or "reported", or leave them out.
- Write everything in your own words. Never copy article text, and never use photos or screenshots from news sites. Text graphics only.
- If no reliable fresh news exists, make a second evergreen post instead of guessing.

## Steps each night

1. Clone the repo (`posts` branch). Read `HISTORY.md` and this playbook.
2. Work out tomorrow's date and weekday in IST. Research both posts.
3. Write a small script that `import`s `tools/techumachi.py` (add `tools/` to sys.path) and builds the slides with its helpers. Copy layouts from the `build_*` examples.
4. Render, then **look at every slide** (Read the images). Fix any text that overflows a card or touches the footer.
5. Make the Reel: `python3 tools/reel.py YYYY-MM-DD/<name>_reel.mp4 <the 7 PM slides in order>`. Extract a few frames with ffmpeg and look at them. Delete `tools/__pycache__/` afterwards.
6. Copy the images, the Reel and its cover into `YYYY-MM-DD/`, commit, and push to `posts`.
7. Schedule both carousels with Metricool `createScheduledPost` (blogId 7591592; 13:00 and 19:00 IST tomorrow; the media list is the raw URLs in slide order).
8. Schedule the Reel at 21:00 IST tomorrow: media = the raw `.mp4` URL, `videoThumbnailUrl` = the raw `_cover.jpg` URL, `instagramData` = `{"type": "REEL", "showReelOnFeed": true, "isAiGenerated": false}`. Caption: a shorter version of the 7 PM caption (same 5 hashtags and brand handle).
9. Append the posts (date, slot, topic, hashtags, sources) to `HISTORY.md` (the Reel as one row with slot 21:00 and topic "Reel of 19:00 post"), commit, and push.
10. Send the owner a short message: tomorrow's two topics, the times (1 PM, 7 PM, Reel at 9 PM), and that all three are scheduled. Also report any failure.
