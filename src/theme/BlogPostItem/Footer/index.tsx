import React, {type ReactNode} from 'react';
import {useBlogPost} from '@docusaurus/plugin-content-blog/client';
import EditMetaRow from '@theme/EditMetaRow';
import ReadMoreLink from '@theme/BlogPostItem/Footer/ReadMoreLink';

/**
 * 标签已在 Header 标题下展示，这里只保留编辑信息与列表页的“阅读全文”。
 */
export default function BlogPostItemFooter(): ReactNode {
  const {metadata, isBlogPostPage} = useBlogPost();
  const {title, editUrl, hasTruncateMarker, lastUpdatedBy, lastUpdatedAt} =
    metadata;

  if (isBlogPostPage) {
    const canDisplayEditMetaRow = !!(editUrl || lastUpdatedAt || lastUpdatedBy);
    if (!canDisplayEditMetaRow) return null;

    return (
      <footer className="docusaurus-mt-lg">
        <EditMetaRow
          className="margin-top--sm"
          editUrl={editUrl}
          lastUpdatedAt={lastUpdatedAt}
          lastUpdatedBy={lastUpdatedBy}
        />
      </footer>
    );
  }

  const truncatedPost = hasTruncateMarker;
  if (!truncatedPost) return null;

  return (
    <footer className="row docusaurus-mt-lg">
      <div className="col text--right">
        <ReadMoreLink blogPostTitle={title} to={metadata.permalink} />
      </div>
    </footer>
  );
}
