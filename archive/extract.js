import fs from "fs";
import fetch from "node-fetch";

let data = JSON.parse(
  fs.readFileSync(
    "/Users/maxbittker/Downloads/twitter-2022-06-23-385f3d9e6764f3ee077c85dc995c675e3fa3bf4c17df59e6bed905c9788a25b9/data/tweet.js"
  )
);

let dataWhere = JSON.parse(
  fs.readFileSync(
    "/Users/maxbittker/Downloads/twitter-2022-06-24-4561460de80ef4875439908a306745d12eafad28e28f734a3b68bffab9cbaec5/data/tweet.js"
  )
);

const parseTitle = (body) => {
  let match = body.match(/<title data-rh="true">([^<]*)<\/title>/); // regular expression to parse contents of the <title> tag
  if (!match || typeof match[1] !== "string")
    throw new Error("Unable to parse the title tag");
  return match[1];
};
async function urlToTitle(url) {
  return fetch(url, {
    headers: {
      "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
  })
    .then(async (res) => {
      let text = await res.text();
      console.log(text.slice(0, 500));
      let title = parseTitle(text);
      console.log(title);
      return title;
    })
    .catch((e) => console.error(e.message)); // catch possible errors
}
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

data = data
  .map(({ tweet }) => tweet)
  .filter((a) => new Date(a.created_at) > new Date("Oct 15, 2017"));

let pdata = [];

for (var i = 0; i < data.length; i++) {
  let { full_text, favorite_count, retweet_count, created_at, id } = data[i];
  let whereData = dataWhere.find(({ tweet }) => {
    return tweet.in_reply_to_status_id_str === id;
  });
  let url = whereData?.tweet.entities.urls[0].expanded_url;

  let title = await urlToTitle(url);
  if (title) {
    await delay(3000);
  }
  console.log(url, title);
  console.log(i + "/" + data.length);

  pdata.push({
    id,
    full_text,
    favorite_count,
    retweet_count,
    created_at,
    url: url,
    title: title,
    context: whereData?.tweet.full_text
  });
}

pdata.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

fs.writeFileSync("./archive/nyt_first_said.json", JSON.stringify(pdata));
pdata.sort((a, b) => {
  let as = parseInt(a.favorite_count) + parseInt(a.retweet_count);
  let bs = parseInt(b.favorite_count) + parseInt(b.retweet_count);
  return bs - as;
});

fs.writeFileSync("./archive/sorted_nyt_first_said.json", JSON.stringify(pdata));
