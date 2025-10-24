# [@NYT_first_said](https://twitter.com/NYT_first_said)

#### [Info website](https://maxbittker.github.io/nyt-first-said/)

A twitter bot to track when the New York Times publishes a word for the first time in history.
running at: [@NYT_first_said](https://twitter.com/NYT_first_said)

It also powers a sibling bot [@NYT_said_where](https://twitter.com/NYT_said_where), which replies to each tweet with a few words of source-text context, and a link to the article.

The code takes some steps to throw away un-interesting words like proper nouns and urls, but still picks up a lot of typos and nonsense, so the sanitization is an ongoing process.

Some points of inspiration are Allison Parrish's @everyword bot, and the [NewsDiffs](http://newsdiffs.org/about/) editorial change archiving software.

## Basic architecture

NYT-first-said is essentially a single script. It's running once an hour as a cron job on a small VPS.

`nyt.py` is a beautifulsoup parser adapted from the [newsdiffs sourcecode](https://github.com/ecprice/newsdiffs).

`redis` holds a list of scraped URLs and seen words (to reduce load on NYT API). It also holds a count of words tweeted recently to avoid blasting out too many tweets in a short period of time.

`api_check.py` uses the [NYT article_search API](https://developer.nytimes.com/) to check through all digitized NYT history to be confident this is really the first occurrence of a word. It returns weird 500s for some words. If you know why let me know.

`simple_scrape.py` Checks for new article urls, retrieves the article text using `nyt.py`, splits them into words, and then determines whether each word is fit to tweet using (in this order) some heuristics to discard unwanted types of words, uniqueness in our local redis instance, and finally uniqueness against the article_search api. If all of these checks pass, it tweets the word, and replies with the context and link.


Also check out [@nyt-finally-said](https://github.com/uniphil/nyt-finally-said), a cool sibling bot that cross-references these words with the google n-gram dataset!

# Running locally

- Create a `.env` file in the project root that looks like this:

        S3A=<Your S3-like archive.org key from https://archive.org/account/s3.php>
        WORDNIK_API_KEY=<Your Wordnik API key>

- Set up a virtual Python environment:
    - `python3 -m venv venv`
    - `source venv/bin/activate`
- Install Python packages with `pip install -r requirements.txt`.
- Download data needed by `textblob` with `make install-textblob`.
- Run `. tools/init-aws.sh` (the space after the . is important) to set the AWS_PROFILE env. var. If you haven't already, use [`aws configure --wordnik](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-using-profiles) to create configuration and credential files for the `wordnik` profile.
- Run the main program with `python simple_scrape.py`
    - To get stdout and error logs captured in text files, run `./tools/scrape-site.py <site name from data/target_sites.json>`

# AWS lambda

There is also a lambda in this project that listens for the sentence objects to drop in the [nyt-said-sentences bucket](https://054978852993-rpuykha7.us-west-1.console.aws.amazon.com/s3/buckets/nyt-said-sentences?region=us-west-1&bucketType=general&tab=objects). The lambda uploads those objects to S3.

## Setting up

To run the parts of the project that use AWS from your computer, you need to set up a file at `~/.aws/credentials` that has your access keys in it like so:

    [default]
    aws_access_key_id = <access key>
    aws_secret_access_key = <secret>


### aws tool

To deploy the lambda from your computer, you'll need to [install the `aws` tool](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

## Deploying

You can deploy changes to the lambda on AWS with the `push-sentences-to-elastic` Makefile target.

That will create a zip file with the relevant files, then push it to AWS with the `aws` command line tool.

# Tests

Run tests with `make run-test`.

# Exploratory tools

You can try out the NYT parser with `python try_parser.py <NYT url>`.

# Running in development

Use `./tools/scrape-site.sh <site id from target_sites.json` to run locally.

# Scheduled runs

The script runs on GitHub Actions.

The definition for the runner action is in `brush.yml`. It takes an input named `site` that corresponds to a key in `data/target_sites.json`. That input tells the action what which site `simple_scrape.py` should run on.

`daily_launcher.yml` defines when the Brush action runs. It is generated vi`make generate-launcher`.
