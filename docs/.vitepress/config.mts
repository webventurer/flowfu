import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'stride',
  description: 'All the speed. None of the mess. Claude Code skills for atomic commits and Linear workflow.',
  base: '/stride/',
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/getting-started' },
      { text: 'Skills', items: [
        { text: '/commit', link: '/skills/commit' },
        { text: '/linear', link: '/skills/linear' },
        { text: '/craft', link: '/skills/craft' },
      ]},
      { text: 'GitHub', link: 'https://github.com/webventurer/stride' },
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Getting started', link: '/getting-started' },
          { text: 'How it works', link: '/how-it-works' },
          { text: 'Install', link: '/install' },
        ],
      },
      {
        text: 'Skills',
        items: [
          { text: '/commit — Atomic commits', link: '/skills/commit' },
          { text: '/linear — Linear workflow', link: '/skills/linear' },
          { text: '/craft — Prompt generation', link: '/skills/craft' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'Agentic engineering', link: '/reference/agentic-engineering' },
          { text: 'Kanban process', link: '/reference/kanban' },
          { text: 'Issue statuses', link: '/reference/issue-statuses' },
          { text: 'Issue template', link: '/reference/issue-template' },
          { text: 'Chris Beams commit style', link: '/reference/commit-style' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/webventurer/stride' },
    ],
  },
})
