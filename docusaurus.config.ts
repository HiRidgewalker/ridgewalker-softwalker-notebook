import {themes as prismThemes} from 'prism-react-renderer';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import type {PluginOptions} from '@docusaurus/plugin-content-docs';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

/**
 * 侧边栏文档条目直接显示文件名，与 docs/ 下的源文件名保持同步。
 * 分类标签仍取自 _category_.json；显式设置的 sidebar_label（如首页）优先。
 */
const syncSidebarLabelsWithFilenames: NonNullable<
  PluginOptions['sidebarItemsGenerator']
> = async ({defaultSidebarItemsGenerator, ...args}) => {
  type SidebarItems = Awaited<
    ReturnType<typeof defaultSidebarItemsGenerator>
  >;

  const rewrite = (sidebarItems: SidebarItems): SidebarItems =>
    sidebarItems.map((item) => {
      if (item.type === 'doc') {
        if (item.label !== undefined) return item;
        const filename = item.id.split('/').pop();
        return filename ? {...item, label: filename} : item;
      }
      if (item.type === 'category') {
        return {...item, items: rewrite(item.items)};
      }
      return item;
    });

  return rewrite(await defaultSidebarItemsGenerator(args));
};

const config: Config = {
  title: 'Software Tech Notebook',
  tagline: 'Personal software technology notebook',
  favicon: 'img/favicon.svg',

  url: 'https://software-tech-notebook.lovefreedom1128.workers.dev',
  baseUrl: '/',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  clientModules: [require.resolve('./src/clientModules/katex.ts')],

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
          sidebarItemsGenerator: syncSidebarLabelsWithFilenames,
          showLastUpdateTime: true,
          breadcrumbs: true,
          remarkPlugins: [remarkMath],
          rehypePlugins: [[rehypeKatex, {throwOnError: false, strict: false}]],
        },
        blog: {
          showReadingTime: true,
          blogTitle: 'Tech Blog',
          blogDescription: '跨技术选型、方案与架构笔记',
          postsPerPage: 10,
          blogSidebarTitle: '全部文章',
          blogSidebarCount: 'ALL',
          onUntruncatedBlogPosts: 'ignore',
          remarkPlugins: [remarkMath],
          rehypePlugins: [[rehypeKatex, {throwOnError: false, strict: false}]],
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Software Tech Notebook',
      items: [
        {to: '/', label: 'Tech Notebook', position: 'left'},
        {to: '/blog', label: 'Tech Blog', position: 'left'},
        {type: 'search', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Software Tech Notebook · ${new Date().getFullYear()}`,
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
