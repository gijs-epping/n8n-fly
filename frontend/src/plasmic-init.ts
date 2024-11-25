import { initPlasmicLoader } from "@plasmicapp/loader-react";

export const PLASMIC = initPlasmicLoader({
  projects: [
    {
      id: "p41xhVExBoDuAHBPkXb1p1",  // ID from the plasmic.md file
      token: "i7Mll1LDifAnPmAQNw1D0OqOKCU98ESyuwoodLdUuYvshgwsX5SZ3mIY00C30UASzJl6A9HjfcAduzFQBvvw"  // Token from the plasmic.md file
    }
  ],
  // Fetches the latest revisions, whether or not they were unpublished!
  // Disable for production to ensure you render only published changes.
  preview: true,
});
