import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'codefu',
  description: 'Claude Code skills for atomic commits and Linear workflow',
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/getting-started' },
      { text: 'Skills', items: [
        { text: '/commit', link: '/skills/commit' },
        { text: '/linear', link: '/skills/linear' },
      ]},
      { text: 'GitHub', link: 'https://github.com/webventurer/codefu-core' },
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Getting started', link: '/getting-started' },
          { text: 'Install', link: '/install' },
        ],
      },
      {
        text: 'Skills',
        items: [
          { text: '/commit — Atomic commits', link: '/skills/commit' },
          { text: '/linear — Linear workflow', link: '/skills/linear' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'Kanban process', link: '/reference/kanban' },
          { text: 'Chris Beams commit style', link: '/reference/commit-style' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/webventurer/codefu-core' },
    ],
  },
})
