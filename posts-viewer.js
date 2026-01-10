/**
 * Posts Viewer Component
 * Loads and renders all markdown posts from the post_markdown directory
 */

class PostsViewer {
    constructor(containerId) {
        this.containerId = containerId;
        this.posts = [];
        this.marked = null;
    }

    /**
     * Initialize the posts viewer
     */
    async init() {
        // Load marked.js for markdown rendering
        if (typeof marked === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/marked/marked.min.js');
        }
        this.marked = marked;
        
        // Configure marked options
        this.marked.setOptions({
            breaks: true,
            gfm: true,
            headerIds: true,
            mangle: false
        });

        // Load and render posts
        await this.loadPosts();
        this.render();
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
     * Load all markdown posts from the post_markdown directory
     */
    async loadPosts() {
        try {
            // Get list of markdown files
            // Note: This requires a server-side endpoint or a list of files
            // For now, we'll try to fetch known files or use a directory listing
            
            // Try to fetch a posts manifest or list files
            const response = await fetch('post_markdown/manifest.json').catch(() => null);
            
            if (response && response.ok) {
                const manifest = await response.json();
                const files = manifest.files || [];
                
                for (const file of files) {
                    await this.loadPost(file);
                }
            } else {
                // Fallback: Try to discover markdown files by attempting common patterns
                // This is a best-effort approach since we can't list directories in static sites
                console.warn('manifest.json not found. Attempting to discover markdown files...');
                
                // Try common filenames or show error
                this.showError('manifest.json not found. Please ensure the download script has created it, or manually create post_markdown/manifest.json with a list of markdown files.');
            }
        } catch (error) {
            console.error('Error loading posts:', error);
            this.showError('Failed to load posts. Please check the console for details.');
        }
    }

    /**
     * Load a single markdown post
     */
    async loadPost(filename) {
        try {
            const response = await fetch(`post_markdown/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error(`Failed to load ${filename}: ${response.statusText}`);
            }
            
            const markdown = await response.text();
            
            // Extract title from first heading or filename
            const titleMatch = markdown.match(/^#\s+(.+)$/m);
            const title = titleMatch ? titleMatch[1] : filename.replace('.md', '');
            
            // Process image references - convert to use chart_images directory
            const processedHtml = this.processImages(markdown);
            
            this.posts.push({
                filename,
                title,
                html: processedHtml,
                rawMarkdown: markdown
            });
        } catch (error) {
            console.error(`Error loading post ${filename}:`, error);
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
     * Render all posts to the container
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        if (this.posts.length === 0) {
            container.innerHTML = '<p class="no-posts">No posts found.</p>';
            return;
        }

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
                    <p class="posts-count">${this.posts.length} post${this.posts.length !== 1 ? 's' : ''}</p>
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

