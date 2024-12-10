from Scripts import resource_fetcher
from Scripts import utils
import random

class Github:
    def __init__(self):
        self.utils = utils.Utils()
        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.fetcher = resource_fetcher.ResourceFetcher(self.headers)
        
    def get_latest_commit(self, owner, repo, branch="main"):
        url = "https://github.com/{}/{}/commits/{}".format(owner, repo, branch)

        response = self.fetcher.fetch_and_parse_content(url)

        for line in response.splitlines():
            if "href=\"" in line and "/commit/" in line and "title=\"" in line:
                sha = line.split("href=\"", 1)[1].split("\"", 1)[0].split("/commit/")[-1]
                try:
                    message = line.split("title=\"", 1)[1].split("\"", 1)[0]
                except:
                    message = line.split(sha)[1].split(">", 1)[1].split("<")[0]

                return {
                    "message": message,
                    "sha": sha
                }
                
        return None

    def get_latest_release(self, owner, repo):
        url = "https://github.com/{}/{}/releases".format(owner, repo)
        response = self.fetcher.fetch_and_parse_content(url)

        body = ""
        tag_name = None
        assets = []
        
        for line in response.splitlines():
            if "<a" in line and "href=\"" in line and "/releases/tag/" in line and not tag_name:
                tag_name = line.split("/releases/tag/")[1].split("\"")[0]
            elif "<div" in line and "body-content" in line:
                body = response.split(line.split(">", 1)[0], 1)[1].split("</div>", 1)[0][1:]
                break

        release_tag_url = "https://github.com/{}/{}/releases/expanded_assets/{}".format(owner, repo, tag_name)
        response = self.fetcher.fetch_and_parse_content(release_tag_url)

        for line in response.splitlines():
            if "<a" in line and "href=\"" in line and "/releases/download" in line:
                download_link = line.split("href=\"", 1)[1].split("\"", 1)[0]

                if "tlwm" in download_link or ("tlwm" not in download_link and "DEBUG" not in download_link.upper()):
                    asset_data = response.split(line)[1].split("</div>", 2)[1]

                    try:
                        asset_id = "".join(char for char in asset_data.split("datetime=\"")[-1].split("\"")[0][::-1] if char.isdigit())[:9]
                    except:
                        asset_id = "".join(random.choices('0123456789', k=9))

                    assets.append({
                        "product_name": self.extract_asset_name(download_link.split("/")[-1]), 
                        "id": int(asset_id), 
                        "url": "https://github.com" + download_link
                    })

        return {
            "body": body,
            "assets": assets
        }
    
    def extract_asset_name(self, file_name):
        end_idx = len(file_name)
        if "-" in file_name:
            end_idx = min(file_name.index("-"), end_idx)
        if "_" in file_name:
            end_idx = min(file_name.index("_"), end_idx)
        if "." in file_name:
            end_idx = min(file_name.index("."), end_idx)
            if file_name[end_idx] == "." and file_name[end_idx - 1].isdigit():
                end_idx = end_idx - 1
        asset_name = file_name[:end_idx]

        if "Sniffer" in file_name:
            asset_name = file_name.split(".")[0]
        if "unsupported" in file_name:
            asset_name += "-unsupported"
        elif "rtsx" in file_name:
            asset_name += "-rtsx"
        elif "itlwm" in file_name.lower():
            if "Sonoma14.4" in file_name:
                asset_name += "23.4"
            elif "Sonoma14.0" in file_name:
                asset_name += "23.0"
            elif "Ventura" in file_name:
                asset_name += "22"
            elif "Monterey" in file_name:
                asset_name += "21"
            elif "BigSur" in file_name:
                asset_name += "20"
            elif "Catalina" in file_name:
                asset_name += "19"
            elif "Mojave" in file_name:
                asset_name += "18"
            elif "HighSierra" in file_name:
                asset_name += "17"

        return asset_name