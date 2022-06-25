import fs from "fs";
import fetch from "node-fetch";

let data = JSON.parse(fs.readFileSync("archive/sorted_nyt_first_said.json"));

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
      // console.log(text.slice(0, 150).replace(/(\r\n|\n|\r)/gm, ""));
      let title = parseTitle(text);
      // console.log(title);
      return title;
    })
    .catch((e) => console.error(e.message)); // catch possible errors
}
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

for (var i = 0; i < data.length; i++) {
  let { url } = data[i];
  if (data[i].title) {
    continue;
  }

  let title = await urlToTitle(url);
  console.log(url, title);

  data[i].title = title;
  if (title) {
    await delay(100);
  }
  if (i % 15 === 0) checkpoint();
  console.log(i + "/" + data.length);
}

function checkpoint() {
  console.log("CHECKPOINT");
  let cData = data.slice();
  let nFilled = cData.filter((a) => a.title).length;
  console.log(nFilled / cData.length);

  cData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  fs.writeFileSync("./archive/nyt_first_said.json", JSON.stringify(cData));
  cData.sort((a, b) => {
    let as = parseInt(a.favorite_count) + parseInt(a.retweet_count);
    let bs = parseInt(b.favorite_count) + parseInt(b.retweet_count);
    return bs - as;
  });

  fs.writeFileSync(
    "./archive/sorted_nyt_first_said.json",
    JSON.stringify(cData)
  );
}
checkpoint();
