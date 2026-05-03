import { defineConfig } from 'vitepress'

const releases = 'https://github.com/atticus-lv/super_io/releases'
const repo = 'https://github.com/atticus-lv/super_io'
const base = process.env.VITEPRESS_BASE ?? '/'

export default defineConfig({
  title: 'Super IO',
  description: 'Clipboard-driven import and export shortcuts for Blender 5',
  base,
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['meta', { name: 'theme-color', content: '#f59e0b' }],
    ['link', { rel: 'icon', href: '/media/logo/logo.png' }]
  ],
  themeConfig: {
    logo: '/media/logo/logo.png',
    search: {
      provider: 'local'
    },
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Custom Config', link: '/guide/custom-config' },
      { text: 'Releases', link: releases }
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Getting Started', link: '/guide/getting-started' },
          { text: 'Import and Export', link: '/guide/import-export' },
          { text: 'How It Works', link: '/guide/how-it-works' }
        ]
      },
      {
        text: 'Custom Config',
        items: [
          { text: 'Config Management', link: '/guide/custom-config' },
          { text: 'Custom Operators', link: '/guide/custom-operators' },
          { text: 'Config Storage', link: '/guide/config-storage' }
        ]
      },
      {
        text: 'Compatibility',
        items: [
          { text: 'Older Blender Versions', link: '/guide/older-blender' }
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: repo }
    ],
    footer: {
      message: 'Released under the GPL-3.0-or-later license.',
      copyright: 'Copyright (c) 2022-2026 Atticus'
    }
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en-US'
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      title: 'Super IO',
      description: '面向 Blender 5 的剪贴板导入导出扩展',
      themeConfig: {
        nav: [
          { text: '指南', link: '/zh/guide/getting-started' },
          { text: '自定义配置', link: '/zh/guide/custom-config' },
          { text: '发布页', link: releases }
        ],
        sidebar: [
          {
            text: '指南',
            items: [
              { text: '快速开始', link: '/zh/guide/getting-started' },
              { text: '导入与导出', link: '/zh/guide/import-export' },
              { text: '工作方式', link: '/zh/guide/how-it-works' }
            ]
          },
          {
            text: '自定义配置',
            items: [
              { text: '配置管理', link: '/zh/guide/custom-config' },
              { text: '自定义操作符', link: '/zh/guide/custom-operators' },
              { text: '配置数据存储', link: '/zh/guide/config-storage' }
            ]
          },
          {
            text: '兼容性',
            items: [
              { text: '旧版 Blender', link: '/zh/guide/older-blender' }
            ]
          }
        ],
        footer: {
          message: '基于 GPL-3.0-or-later 许可发布。',
          copyright: 'Copyright (c) 2022-2026 Atticus'
        }
      }
    }
  }
})
