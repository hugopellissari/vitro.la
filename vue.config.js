const { join } = require('path')

module.exports = {
  lintOnSave: true,
  configureWebpack: {
    devtool: 'source-map'
  },
  css: {
    modules: true,
    sourceMap: true,
    loaderOptions: {
      sass: {
        includePaths: [
          join(__dirname, 'node_modules')
        ]
      }
    }
  },
  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: true
    }
  }
}
