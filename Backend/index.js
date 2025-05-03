const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
app.use(cors());
app.use(express.json());

const BASE_API_URL = 'https://customer.acecloudhosting.com/api/v1/pricing?is_gpu=true&resource=instances';

const regionMapping = {
  mumbai: 'ap-south-mum-1',
  delhi: 'ap-south-del-1',
  noida: 'ap-south-noi-1',
  virginia: 'us-east-at-1',
};

const exchangeRateUSDToINR = 84.58; 
const priceFieldMap = {
  hour: 'price_per_hour',
  month: 'price_per_month',
  half_year: 'price_per_half_year',
  year: 'price_per_year',
  spot: 'price_per_spot'
};

const allPriceFields = [
  'price_per_hour',
  'price_per_month',
  'price_per_half_year',
  'price_per_year',
  'price_per_spot',
];

app.post('/api/recommend-gpus', async (req, res) => {
  const { region, operating_system, budget, timeline } = req.body;

  if (!region || !regionMapping[region.toLowerCase()]) {
    return res.status(400).json({ error: 'Invalid or missing region.' });
  }

  const regionCode = regionMapping[region.toLowerCase()];
  const timelineKey = priceFieldMap[timeline?.toLowerCase()];
  if (!timelineKey) {
    return res.status(400).json({ error: 'Invalid timeline. Use hour, month, half_year, or year.' });
  }

  try {
    const apiUrl = `${BASE_API_URL}&region=${regionCode}`;
    const response = await fetch(apiUrl);
    const result = await response.json();

    if (!Array.isArray(result.data)) {
      return res.status(500).json({ error: 'Invalid data from provider.' });
    }

    const filtered = result.data
      .filter(item => item.operating_system.toLowerCase() === operating_system.toLowerCase())
      .map(item => {
        const currency = item.currency.toUpperCase();
        const timelinePrice = item[timelineKey];

        const convertedTimelinePrice =
          currency === 'USD' ? timelinePrice * exchangeRateUSDToINR : timelinePrice;

        const averagePrice = allPriceFields
          .map(field => {
            const val = item[field];
            return typeof val === 'number' && !isNaN(val)
              ? currency === 'USD' ? val * exchangeRateUSDToINR : val
              : null;
          })
          .filter(v => v !== null);

        const avgPriceInINR =
          averagePrice.length > 0
            ? averagePrice.reduce((a, b) => a + b, 0) / averagePrice.length
            : Infinity;

        return {
          ...item,
          convertedTimelinePrice,
          avgPriceInINR,
        };
      })
      .filter(item => item.convertedTimelinePrice <= budget);


    const topGpus = filtered
      .sort((a, b) =>
        b.ram !== a.ram
          ? b.ram - a.ram
          : b.vcpus - a.vcpus
      )
      .slice(0, 5);

    res.json({
      success: true,
      topGpus,
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch and process GPU data.' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
