const examples = {
  wayfair: {
    label: "Wayfair",
    platformId: 2,
    redisKey: "wayfair_spider:urls",
    method: "POST",
    endpoint: "https://www.wayfair.com/graphql",
    url: "https://www.wayfair.com/office-storage-cabinets/pdp/wade-logan-belak-63-wide-office-storage-cabinets-w110297593.html",
    extract: (url) => (url.split(".html")[0].split("-").pop() || "").trim(),
    ratings: { 5: 184, 4: 61, 3: 18, 2: 7, 1: 5 },
    reviews: [
      ["Jordan M.", 5, "2026-03-18", "Yes", "Clean design and easy assembly"],
      ["Avery", 4, "2026-02-11", "Yes", "Solid storage for a small office"],
      ["Sam P.", 5, "2026-01-30", "No", "Better than expected finish"],
    ],
  },
  homedepot: {
    label: "HomeDepot",
    platformId: 4,
    redisKey: "homedepot_spider:urls",
    method: "POST",
    endpoint: "https://www.homedepot.com/federation-gateway/graphql?opname=reviews",
    url: "https://www.homedepot.com/p/FUFU-GAGA-5-Drawers-White-Makeup-Vanity-Sets-Dressing-Table-Sets-with-LED-Dimmable-Mirror-Stool-and-3-Tier-Storage-Shelves-KF210141-01/318504099",
    extract: (url) => cleanUrl(url).split("/").pop().trim(),
    ratings: { 5: 91, 4: 34, 3: 10, 2: 4, 1: 3 },
    reviews: [
      ["DIYHome", 5, "2026-04-04", "Yes", "Great value for the room"],
      ["Morgan", 4, "2026-03-02", "Yes", "Instructions could be clearer"],
      ["Lee", 3, "2026-01-19", "No", "Looks good after setup"],
    ],
  },
  lowes: {
    label: "Lowes",
    platformId: 6,
    redisKey: "lowes_spider:urls",
    method: "GET",
    endpoint: "https://www.lowes.com/rnr/r/get-by-product/{product_id}",
    url: "https://www.lowes.com/pd/FUFU-GAGA-3-Blades-Retro-Wood-Ceiling-Fan/5015392509?idProductFound=false&idExtracted=true",
    extract: (url) => cleanUrl(url).split("/").pop().trim(),
    ratings: { 5: 77, 4: 21, 3: 9, 2: 4, 1: 2 },
    reviews: [
      ["Casey", 5, "2026-04-21", "Yes", "Quiet fan with a warm look"],
      ["Taylor", 4, "2026-03-29", "Yes", "Good airflow in a bedroom"],
      ["Robin", 5, "2026-02-14", "Yes", "Matched the product photos"],
    ],
  },
  overstock: {
    label: "Overstock",
    platformId: 5,
    redisKey: "overstock_spider:urls",
    method: "GET",
    endpoint: "https://api.overstock.com/reviews",
    url: "https://www.overstock.com/Home-Garden/1-Panel-Cabinet-Iron-Fireplace-Screen/34166905/product.html?option=64407264",
    extract: (url) => cleanUrl(url).split("/").slice(-2, -1)[0].trim(),
    ratings: { 5: 112, 4: 37, 3: 15, 2: 6, 1: 8 },
    reviews: [
      ["Alex", 5, "2026-03-12", "Yes", "Exactly the size listed"],
      ["Riley", 4, "2026-02-26", "No", "Sturdy and shipped quickly"],
      ["Jamie", 5, "2026-01-07", "Yes", "Nice detail for the price"],
    ],
  },
};

const platformSelect = document.querySelector("#platform");
const urlInput = document.querySelector("#product-url");
const simulateButton = document.querySelector("#simulate-btn");
const parsedOutput = document.querySelector("#parsed-output");
const payloadOutput = document.querySelector("#payload-output");
const ratingChart = document.querySelector("#rating-chart");
const reviewTable = document.querySelector("#review-table");
const statusSteps = [...document.querySelectorAll(".status-strip span")];

function cleanUrl(url) {
  return url.split("?")[0].split("#")[0];
}

function stableId(platformId, productId) {
  let hash = 0;
  const input = `${platformId}_${productId}`;
  for (let index = 0; index < input.length; index += 1) {
    hash = (hash << 5) - hash + input.charCodeAt(index);
    hash |= 0;
  }
  return `demo-${Math.abs(hash).toString(16)}`;
}

function buildPayload(config, productId) {
  const uuid = stableId(config.platformId, productId);
  return {
    redis_key: config.redisKey,
    job: {
      url: config.endpoint.replace("{product_id}", productId),
      method: config.method,
      product_id: productId,
      uuid,
      is_first_time: true,
      headers: {
        accept: "application/json",
        "user-agent": "Generated desktop user agent",
      },
      pagination: {
        start_index: 1,
        review_limit: 100,
      },
    },
  };
}

function renderParsed(config, productId) {
  parsedOutput.innerHTML = "";
  const rows = [
    ["Platform", config.label],
    ["Platform ID", config.platformId],
    ["Product ID", productId || "Unable to parse"],
    ["Redis key", config.redisKey],
  ];

  rows.forEach(([label, value]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = value;
    parsedOutput.append(dt, dd);
  });
}

function renderRatings(ratings) {
  ratingChart.innerHTML = "";
  const max = Math.max(...Object.values(ratings));
  [5, 4, 3, 2, 1].forEach((star) => {
    const count = ratings[star];
    const row = document.createElement("div");
    row.className = "rating-row";
    row.innerHTML = `
      <strong>${star} star</strong>
      <div class="bar-track"><div class="bar-fill" style="width: ${(count / max) * 100}%"></div></div>
      <span>${count}</span>
    `;
    ratingChart.append(row);
  });
}

function renderReviews(reviews) {
  reviewTable.innerHTML = "";
  reviews.forEach(([reviewer, rating, date, verified, title]) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${reviewer}</td>
      <td>${rating}.0</td>
      <td>${date}</td>
      <td>${verified}</td>
      <td>${title}</td>
    `;
    reviewTable.append(row);
  });
}

function advanceStatus() {
  statusSteps.forEach((step) => step.classList.remove("active"));
  statusSteps[0].classList.add("active");
  statusSteps.forEach((step, index) => {
    window.setTimeout(() => {
      statusSteps.forEach((item, activeIndex) => {
        item.classList.toggle("active", activeIndex <= index);
      });
    }, index * 260);
  });
}

function runSimulation() {
  const config = examples[platformSelect.value];
  const productId = config.extract(urlInput.value);
  const payload = buildPayload(config, productId);

  renderParsed(config, productId);
  payloadOutput.textContent = JSON.stringify(payload, null, 2);
  renderRatings(config.ratings);
  renderReviews(config.reviews);
  advanceStatus();
}

platformSelect.addEventListener("change", () => {
  urlInput.value = examples[platformSelect.value].url;
  runSimulation();
});

simulateButton.addEventListener("click", runSimulation);

urlInput.value = examples[platformSelect.value].url;
runSimulation();
