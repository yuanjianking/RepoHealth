export default {
  '*.{js,jsx,ts,tsx}': ['eslint --fix', 'prettier --write'],
  '*.{json,md,css,scss}': ['prettier --write'],
  'src/**/*.{test,spec}.{js,jsx,ts,tsx}': ['vitest related --run'],
};
