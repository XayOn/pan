const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  publicPath: process.env.BASE_URL ? process.env.BASE_URL + '/' : '/',
  transpileDependencies: true
})
