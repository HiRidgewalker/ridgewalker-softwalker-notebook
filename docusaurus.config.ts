import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Software Tech Notebook',
  tagline: '个人软件技术知识库',
  favicon: 'img/favicon.svg',

  url: 'https://notebook.local',
  baseUrl: '/',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  markdown: {
    // 全部笔记为纯 CommonMark，不走 MDX，避免 {} 被误判为 JSX
    format: 'md',
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['zh', 'en'],
        indexDocs: true,
        indexBlog: false,
        indexPages: false,
        docsRouteBasePath: '/',
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'docs',
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          // 保留文件名开头的数字/罗马数字前缀，避免 doc id 被改写
          numberPrefixParser: false,
          showLastUpdateTime: true,
          breadcrumbs: true,
        },
        blog: {
          showReadingTime: true,
          blogTitle: '跨技术主题',
          blogDescription: '跨技术选型、方案与架构笔记',
          postsPerPage: 10,
          blogSidebarTitle: '全部文章',
          blogSidebarCount: 'ALL',
          onUntruncatedBlogPosts: 'ignore',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: '技术知识库',
      items: [
        {to: '/', label: '全部笔记', position: 'left'},
        {to: '/blog', label: '跨技术主题', position: 'left'},
        {type: 'search', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: `技术知识库 · ${new Date().getFullYear()}`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: [
        'bash',
        'go',
        'python',
        'typescript',
        'javascript',
        'json',
        'yaml',
        'sql',
        'docker',
        'nginx',
        'ini',
        'toml',
        'java',
        'rust',
        'cpp',
        'diff',
        'http',
      ],
    },
    mermaid: {
      options: {
        theme: {light: 'neutral', dark: 'dark'},
      },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
