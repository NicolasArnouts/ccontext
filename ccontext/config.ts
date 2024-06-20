
import { Config } from "./src/config";

export const defaultConfig: Config = {
  "url": "https://vuejs.org/v2/guide/",
  "match": [
    "https://vuejs.org/v2/guide/**"
  ],
  "maxPagesToCrawl": 100,
  "outputFileName": "vue_js.json",
  "maxTokens": 2000000
};
