/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    reactRemoveProperties: false,
  },
}

module.exports = nextConfig

