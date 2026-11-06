import React, {type CSSProperties, type ReactNode} from 'react';
import Link from '@docusaurus/Link';
import clsx from 'clsx';
import styles from './styles.module.css';

type Props = {
  permalink: string;
  label: string;
  count?: number;
  description?: string;
};

/** 常用技术栈的固定色相，保证品牌感；未列出的按标签名哈希取色 */
const HUE_OVERRIDES: Record<string, number> = {
  MySQL: 200,
  PostgreSQL: 217,
  SQLite: 190,
  MongoDB: 140,
  Redis: 4,
  RabbitMQ: 28,
  Kafka: 260,
  Docker: 210,
  Kubernetes: 220,
  Harbor: 205,
  Jenkins: 24,
  Git: 16,
  Linux: 45,
  Nginx: 145,
  FastAPI: 165,
  Django: 150,
  Celery: 100,
  Python: 210,
  Go: 190,
  JavaScript: 45,
  TypeScript: 211,
  CSS: 220,
  React: 195,
  'Next.js': 0,
  Agent: 280,
  MCP: 300,
  'Prompt Engineering': 320,
  'AI Coding Assistants': 265,
  'Model & Inference Platform': 250,
  鉴权: 340,
  OpenCompass: 210,
  EvalScope: 280,
};

function hashHue(label: string): number {
  let hash = 0;
  for (let i = 0; i < label.length; i++) {
    hash = (hash * 31 + label.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) % 360;
}

function hueOf(label: string): number {
  return HUE_OVERRIDES[label] ?? hashHue(label);
}

export default function Tag({
  permalink,
  label,
  count,
  description,
}: Props): ReactNode {
  const style = {'--tag-hue': hueOf(label)} as CSSProperties;

  return (
    <Link
      rel="tag"
      href={permalink}
      title={description}
      style={style}
      className={clsx(styles.tag, count ? styles.tagWithCount : styles.tagRegular)}>
      {label}
      {count ? <span className={styles.count}>{count}</span> : null}
    </Link>
  );
}
