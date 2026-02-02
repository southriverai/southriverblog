/**
 * Posts Viewer Component
 * Loads and renders all markdown posts from the post_markdown directory
 */

/**
 * Convert slug to title (e.g. "the-speed-to-fly" -> "The Speed To Fly")
 */
function slugToTitle(slug) {
    return slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

class PostsViewer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.posts = [];
        this.marked = null;
        this.listOnly = !!options.listOnly;
    }

    /**
     * Initialize the posts viewer (list of titles on landing, or single post by slug)
     */
    async init() {
        if (typeof marked === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/marked/marked.min.js');
        }
        this.marked = marked;
        this.marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: true,
            mangle: false
        });

        if (this.listOnly) {
            await this.loadPostList();
            this.renderList();
        } else {
            await this.loadPosts();
            this.render();
        }
    }

    /**
     * Initialize single-post view by slug (for post.html?slug=...)
     */
    async initSingle(slug) {
        if (typeof marked === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/marked/marked.min.js');
        }
        this.marked = marked;
        this.marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: true,
            mangle: false
        });
        await this.loadPost(slug + '.md', this.getPostMarkdownBase());
        this.renderSingle();
    }

    /**
     * Load only the manifest and build list of { slug, title } for landing
     */
    async loadPostList() {
        try {
            const base = this.getPostMarkdownBase();
            const manifestUrl = new URL('manifest.json', base);
            manifestUrl.searchParams.set('t', Date.now());
            const response = await fetch(manifestUrl, { cache: 'no-store' }).catch(() => null);
            if (response && response.ok) {
                const manifest = await response.json();
                const files = manifest.files || [];
                this.posts = files.map(filename => {
                    const slug = filename.replace(/\.md$/i, '');
                    return { slug, title: slugToTitle(slug) };
                });
            } else {
                this.showError('manifest.json not found.');
            }
        } catch (error) {
            this.showError('Failed to load posts.');
        }
    }

    /**
     * Dynamically load a script
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Base URL for post_markdown (works when site is in a subpath, e.g. GitHub Pages or localhost subdir)
     */
    getPostMarkdownBase() {
        return new URL('post_markdown/', window.location.href).href;
    }

    /**
     * Load all markdown posts from the post_markdown directory
     */
    async loadPosts() {
        try {
            const base = this.getPostMarkdownBase();
            const manifestUrl = new URL('manifest.json', base);
            manifestUrl.searchParams.set('t', Date.now());

            const response = await fetch(manifestUrl, { cache: 'no-store' }).catch(() => null);

            if (response && response.ok) {
                const manifest = await response.json();
                const files = manifest.files || [];

                for (const file of files) {
                    await this.loadPost(file, base);
                }
            } else {
                this.showError('manifest.json not found. Please ensure the download script has created it, or manually create post_markdown/manifest.json with a list of markdown files.');
            }
        } catch (error) {
            this.showError('Failed to load posts. Please check the console for details.');
        }
    }

    /**
     * Load a single markdown post
     * @param {string} filename - e.g. "post.md"
     * @param {string} [base] - base URL for post_markdown (from getPostMarkdownBase())
     */
    async loadPost(filename, base) {
        const postBase = base ?? this.getPostMarkdownBase();
        const url = new URL(filename, postBase);
        url.searchParams.set('t', Date.now());

        try {
            const response = await fetch(url, { cache: 'no-store' });
            if (!response.ok) {
                throw new Error(`${response.status} ${response.statusText}`);
            }

            const markdown = await response.text();

            const titleMatch = markdown.match(/^#\s+(.+)$/m);
            const title = titleMatch ? titleMatch[1] : filename.replace('.md', '');

            const processedHtml = this.processImages(markdown);

            this.posts.push({
                filename,
                title,
                html: processedHtml,
                rawMarkdown: markdown
            });
        } catch (error) {
            // Skip failed posts
        }
    }

    /**
     * Process image references in markdown
     * Converts plain text image filenames to markdown image syntax and proper paths
     */
    processImages(markdown) {
        // First, process the raw markdown to convert plain text image references
        // Look for lines that are just image filenames (like "fossil fuel.png")
        // This pattern matches lines that contain only an image filename
        const lines = markdown.split('\n');
        const processedLines = lines.map(line => {
            const trimmed = line.trim();
            // Check if line is just an image filename
            const imagePattern = /^[\w\s\-]+\.(png|jpg|jpeg|gif)$/i;
            if (imagePattern.test(trimmed)) {
                // Convert to markdown image syntax
                return `![${trimmed}](chart_images/${trimmed})`;
            }
            return line;
        });
        
        const processedMarkdown = processedLines.join('\n');
        
        // Parse markdown to HTML
        let html = this.marked.parse(processedMarkdown);
        
        // Create a temporary DOM element to parse HTML and add styling
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Find all images and ensure proper styling
        const images = tempDiv.querySelectorAll('img');
        images.forEach(img => {
            // Add styling if not already styled
            if (!img.style.maxWidth) {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                img.style.margin = '20px 0';
                img.style.display = 'block';
                img.style.borderRadius = '8px';
                img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
            }
        });
        
        return tempDiv.innerHTML;
    }

    /**
     * Render landing page: list of post titles linking to post.html?slug=...
     */
    renderList() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (this.posts.length === 0) {
            container.innerHTML = '<p class="no-posts">No posts found.</p>';
            return;
        }

        const countNote = `<p class="posts-count">${this.posts.length} post${this.posts.length !== 1 ? 's' : ''}</p>`;
        const listHtml = this.posts.map(({ slug, title }) => {
            const postUrl = new URL('post.html', window.location.href);
            postUrl.searchParams.set('slug', slug);
            return `<li class="post-list-item"><a href="${this.escapeHtml(postUrl.pathname + '?' + postUrl.searchParams.toString())}">${this.escapeHtml(title)}</a></li>`;
        }).join('');

        container.innerHTML = `
            <div class="posts-container">
                <div class="posts-header">
                    <h2>All Posts</h2>
                    ${countNote}
                </div>
                <ul class="post-list">
                    ${listHtml}
                </ul>
            </div>
        `;
    }

    /**
     * Render single post (for post.html)
     */
    renderSingle() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (this.posts.length === 0) {
            container.innerHTML = '<p class="no-posts">Post not found.</p>';
            return;
        }

        const post = this.posts[0];
        if (post.title && typeof document !== 'undefined') {
            document.title = post.title + ' — South River Blog';
        }
        if (typeof history !== 'undefined' && history.replaceState) {
            const slug = (post.filename || '').replace(/\.md$/i, '');
            const canonicalUrl = new URL('post.html', window.location.href);
            canonicalUrl.searchParams.set('slug', slug);
            history.replaceState(null, '', canonicalUrl.pathname + '?' + canonicalUrl.searchParams.toString());
        }
        container.innerHTML = `
            <article class="post">
                <div class="post-content">
                    ${post.html}
                </div>
            </article>
        `;
    }

    /**
     * Render all posts (full content) — used when listOnly is false and not single post
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (this.posts.length === 0) {
            container.innerHTML = '<p class="no-posts">No posts found.</p>';
            return;
        }

        const countNote = `<p class="posts-count">${this.posts.length} post${this.posts.length !== 1 ? 's' : ''}</p>`;
        const postsHtml = this.posts.map((post, index) => `
            <article class="post" data-post-index="${index}">
                <div class="post-content">
                    ${post.html}
                </div>
            </article>
        `).join('');

        container.innerHTML = `
            <div class="posts-container">
                <div class="posts-header">
                    <h2>All Posts</h2>
                    ${countNote}
                </div>
                ${postsHtml}
            </div>
        `;
    }

    /**
     * Show an error message
     */
    showError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `<div class="error-message">${this.escapeHtml(message)}</div>`;
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PostsViewer;
}

