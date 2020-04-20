let fs = require("fs");

let data = JSON.parse(
  fs.readFileSync(
    "/home/max/Downloads/twitter-2020-04-20-385f3d9e6764f3ee077c85dc995c675e3fa3bf4c17df59e6bed905c9788a25b9/data/tweet.js"
  )
);

let pdata = data
  .map(({ tweet }) => tweet)
  .map(({ full_text, favorite_count, retweet_count, created_at }) => ({
    full_text,
    favorite_count,
    retweet_count,
    created_at
  }));

pdata = pdata.filter(a => new Date(a.created_at) > new Date("Oct 15, 2017"));

pdata.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

fs.writeFileSync("./archive/nyt_first_said.json", JSON.stringify(pdata));
pdata.sort((a, b) => {
  let as = parseInt(a.favorite_count) + parseInt(a.retweet_count);
  let bs = parseInt(b.favorite_count) + parseInt(b.retweet_count);
  return bs - as;
});

fs.writeFileSync("./archive/sorted_nyt_first_said.json", JSON.stringify(pdata));
