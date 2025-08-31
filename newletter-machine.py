import praw
import os
import argparse
import textwrap
from dotenv import load_dotenv

def get_reddit_instance():
    """
    Initializes and returns a Reddit instance using credentials
    from environment variables.
    """
    load_dotenv() # Loads environment variables from a .env file if it exists

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        print("🔴 ERROR: Reddit API credentials not found.")
        print("Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT environment variables.")
        print("Check the README.md for instructions.")
        exit(1)

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        # Test the connection
        reddit.user.me()
        print("✅ Successfully authenticated with Reddit API.")
        return reddit
    except Exception as e:
        print(f"🔴 ERROR: Could not authenticate with Reddit. Please check your credentials. Details: {e}")
        exit(1)


def get_newletter_content(reddit, subreddit_name, limit, time_filter, comment_limit):
    """
    Fetches top posts and their top comments from a given subreddit.
    """
    try:
        print(f"\n🔍 Hunting for top {limit} posts in r/{subreddit_name} from the past {time_filter}...")
        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.top(time_filter=time_filter, limit=limit)

        print("-" * 80)

        for i, post in enumerate(top_posts):
            print(f"\n{'='*10} POST #{i+1} {'='*10}")
            print(f"📄 TITLE: {post.title}")
            print(f"👍 SCORE: {post.score}")
            print(f"🔗 URL: {post.url}")
            print("\n💬 TOP COMMENTS:\n")

            # Ensure comments are sorted by top and handle potential issues
            post.comment_sort = "top"
            post.comments.replace_more(limit=0) # Remove "more comments" links

            comments_fetched = 0
            for comment in post.comments:
                if comments_fetched >= comment_limit:
                    break
                if not comment.stickied and comment.body != "[deleted]" and comment.body != "[removed]":
                    # Use textwrap for nice formatting of long comments
                    wrapped_comment = textwrap.fill(comment.body, width=70, initial_indent="    ", subsequent_indent="    ")
                    print(f"  - (Score: {comment.score})")
                    print(wrapped_comment)
                    print("-" * 20)
                    comments_fetched += 1
            
            if comments_fetched == 0:
                print("    No valid comments found for this post.")

            print(f"{'='*30}\n")

    except Exception as e:
        print(f"\n🔴 ERROR: Could not fetch posts from r/{subreddit_name}.")
        print(f"Please ensure the subreddit exists and is public. Details: {e}")


def main():
    """
    Main function to parse arguments and run the scraper.
    """
    parser = argparse.ArgumentParser(
        description="""
        ☕🤖 Reddit Viral Content Machine - A Python script to find top posts and comments from Reddit.
        This tool helps you discover proven viral content ideas to use with AI writers like ChatGPT.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("subreddit", help="The name of the subreddit to scrape (e.g., 'LifeProTips').")
    parser.add_argument(
        "-l", "--limit", type=int, default=5,
        help="Number of top posts to fetch. Default: 5"
    )
    parser.add_argument(
        "-t", "--time", default="month",
        choices=["hour", "day", "week", "month", "year", "all"],
        help="Time filter for top posts. Default: 'month'"
    )
    parser.add_argument(
        "-c", "--comments", type=int, default=3,
        help="Number of top comments to fetch per post. Default: 3"
    )

    args = parser.parse_args()

    reddit = get_reddit_instance()
    get_newletter_content(reddit, args.subreddit, args.limit, args.time, args.comments)

    print("\n✅ All done! Copy the output above and use it with your AI tool.")

if __name__ == "__main__":
    main()
