<script lang="ts">
    import { onMount } from "svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher: { id: number; name: string } | null;
        category: { id: number; name: string } | null;
        starRating?: number;
    }

    interface Category {
        id: number;
        name: string;
        description: string;
        game_count: number;
    }

    interface Publisher {
        id: number;
        name: string;
        description: string;
        game_count: number;
    }

    interface PaginationData {
        current_page: number;
        total_pages: number;
        total_items: number;
        items_per_page: number;
        has_next: boolean;
        has_prev: boolean;
    }

    interface GameListResponse {
        games: Game[];
        pagination: PaginationData;
    }

    export let games: Game[] = [];
    let pagination: PaginationData | null = null;
    let loading = true;
    let error: string | null = null;
    let categories: Category[] = [];
    let publishers: Publisher[] = [];
    let selectedCategoryId: string = '';
    let selectedPublisherId: string = '';
    
    // Pagination state
    let currentPage = 1;
    let itemsPerPage = 20;

    const fetchCategories = async () => {
        try {
            const response = await fetch('/api/categories');
            if(response.ok) {
                categories = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch categories:', err);
        }
    };

    const fetchPublishers = async () => {
        try {
            const response = await fetch('/api/publishers');
            if(response.ok) {
                publishers = await response.json();
            }
        } catch (err) {
            console.error('Failed to fetch publishers:', err);
        }
    };

    const fetchGames = async () => {
        loading = true;
        try {
            let url = '/api/games';
            const params = new URLSearchParams();
            
            if (selectedCategoryId) {
                params.append('category_id', selectedCategoryId);
            }
            if (selectedPublisherId) {
                params.append('publisher_id', selectedPublisherId);
            }
            
            // Add pagination parameters
            params.append('page', currentPage.toString());
            params.append('limit', itemsPerPage.toString());
            
            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await fetch(url);
            if(response.ok) {
                const data: GameListResponse = await response.json();
                games = data.games;
                pagination = data.pagination;
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const clearFilters = () => {
        selectedCategoryId = '';
        selectedPublisherId = '';
        currentPage = 1; // Reset to first page when clearing filters
        fetchGames();
    };

    // Pagination functions
    const goToPage = (page: number) => {
        if (page >= 1 && pagination && page <= pagination.total_pages) {
            currentPage = page;
            fetchGames();
        }
    };

    const nextPage = () => {
        if (pagination && pagination.has_next) {
            currentPage++;
            fetchGames();
        }
    };

    const prevPage = () => {
        if (pagination && pagination.has_prev) {
            currentPage--;
            fetchGames();
        }
    };

    const changeItemsPerPage = (newLimit: number) => {
        itemsPerPage = newLimit;
        currentPage = 1; // Reset to first page when changing items per page
        fetchGames();
    };

    // Generate array of page numbers for pagination display
    const getVisiblePageNumbers = (): number[] => {
        if (!pagination) return [];
        
        const totalPages = pagination.total_pages;
        const current = pagination.current_page;
        const delta = 2; // Number of pages to show on each side of current page
        
        let start = Math.max(1, current - delta);
        let end = Math.min(totalPages, current + delta);
        
        // Adjust range if we're near the beginning or end
        if (end - start + 1 < 2 * delta + 1) {
            if (start === 1) {
                end = Math.min(totalPages, start + 2 * delta);
            } else if (end === totalPages) {
                start = Math.max(1, end - 2 * delta);
            }
        }
        
        const pages: number[] = [];
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        return pages;
    };

    // Reactive statement for active filters
    $: hasActiveFilters = selectedCategoryId !== '' || selectedPublisherId !== '';

    // Watch for filter changes (but not pagination changes)
    $: if (selectedCategoryId !== undefined || selectedPublisherId !== undefined) {
        // Reset to first page when filters change
        if (currentPage !== 1) {
            currentPage = 1;
        } else {
            fetchGames();
        }
    }

    onMount(() => {
        fetchCategories();
        fetchPublishers();
        fetchGames();
    });
</script>

<div>
    <div class="mb-6">
        <h2 class="text-2xl font-medium mb-6 text-slate-100">Featured Games</h2>
        
        <!-- Filter Controls -->
        <div class="mb-6 bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <!-- Top row: Items per page selector and pagination info -->
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
                <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                    <!-- Items per page selector -->
                    <div class="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
                        <label for="items-per-page" class="text-sm font-medium text-slate-300 whitespace-nowrap">Items per page:</label>
                        <select 
                            id="items-per-page"
                            bind:value={itemsPerPage}
                            on:change={() => changeItemsPerPage(itemsPerPage)}
                            class="bg-slate-700/60 border border-slate-600 text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2"
                        >
                            <option value={10}>10</option>
                            <option value={20}>20</option>
                            <option value={50}>50</option>
                        </select>
                    </div>
                </div>
                
                <!-- Pagination info -->
                {#if pagination}
                    <div class="text-sm text-slate-400">
                        Showing {((pagination.current_page - 1) * pagination.items_per_page) + 1}-{Math.min(pagination.current_page * pagination.items_per_page, pagination.total_items)} of {pagination.total_items} games
                    </div>
                {/if}
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                <!-- Category Filter -->
                <div class="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
                    <label for="category-filter" class="text-sm font-medium text-slate-300 whitespace-nowrap">Category:</label>
                    <select 
                        id="category-filter"
                        bind:value={selectedCategoryId}
                        class="bg-slate-700/60 border border-slate-600 text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2 min-w-[160px]"
                    >
                        <option value="">All Categories</option>
                        {#each categories as category}
                            <option value={category.id.toString()}>{category.name} ({category.game_count})</option>
                        {/each}
                    </select>
                </div>

                <!-- Publisher Filter -->
                <div class="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
                    <label for="publisher-filter" class="text-sm font-medium text-slate-300 whitespace-nowrap">Publisher:</label>
                    <select 
                        id="publisher-filter"
                        bind:value={selectedPublisherId}
                        class="bg-slate-700/60 border border-slate-600 text-slate-100 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 px-3 py-2 min-w-[160px]"
                    >
                        <option value="">All Publishers</option>
                        {#each publishers as publisher}
                            <option value={publisher.id.toString()}>{publisher.name} ({publisher.game_count})</option>
                        {/each}
                    </select>
                </div>

                <!-- Clear Filters Button -->
                {#if hasActiveFilters}
                    <button 
                        on:click={clearFilters}
                        class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Clear Filters
                    </button>
                {/if}
            </div>
            
            <!-- Active Filters Indicator -->
            {#if hasActiveFilters}
                <div class="mt-3 pt-3 border-t border-slate-600/50">
                    <div class="flex flex-wrap gap-2 items-center">
                        <span class="text-xs font-medium text-slate-400">Active filters:</span>
                        {#if selectedCategoryId}
                            {@const selectedCategory = categories.find(c => c.id.toString() === selectedCategoryId)}
                            {#if selectedCategory}
                                <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300">
                                    Category: {selectedCategory.name}
                                </span>
                            {/if}
                        {/if}
                        {#if selectedPublisherId}
                            {@const selectedPublisher = publishers.find(p => p.id.toString() === selectedPublisherId)}
                            {#if selectedPublisher}
                                <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300">
                                    Publisher: {selectedPublisher.name}
                                </span>
                            {/if}
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
    </div>
    
    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-slate-700 rounded w-full mb-3"></div>
                            <div class="h-3 bg-slate-700 rounded w-5/6 mb-4"></div>
                            <div class="h-2 bg-slate-700 rounded-full w-full mb-2"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if games.length === 0}
        <!-- no games found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">No games available at the moment.</p>
        </div>
    {:else}
        <!-- game list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <a 
                    href={`/game/${game.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                    data-testid="game-card"
                    data-game-id={game.id}
                    data-game-title={game.title}
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
                            
                            {#if game.category || game.publisher}
                                <div class="flex gap-2 mb-3">
                                    {#if game.category}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                                            {game.category.name}
                                        </span>
                                    {/if}
                                    {#if game.publisher}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                                            {game.publisher.name}
                                        </span>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
                            
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
    
    <!-- Pagination Controls -->
    {#if pagination && pagination.total_pages > 1}
        <div class="mt-8 flex flex-col sm:flex-row gap-4 items-center justify-center">
            <!-- Previous Button -->
            <button 
                on:click={prevPage}
                disabled={!pagination.has_prev}
                class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 
                       {pagination.has_prev 
                         ? 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg hover:shadow-blue-600/20' 
                         : 'bg-slate-700 text-slate-400 cursor-not-allowed'}"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Previous
            </button>
            
            <!-- Page Numbers -->
            <div class="flex flex-wrap gap-2 items-center">
                {#if pagination.current_page > 3}
                    <button 
                        on:click={() => goToPage(1)}
                        class="px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 
                               bg-slate-700/60 hover:bg-slate-600 text-slate-300 hover:text-white"
                    >
                        1
                    </button>
                    {#if pagination.current_page > 4}
                        <span class="text-slate-400">...</span>
                    {/if}
                {/if}
                
                {#each getVisiblePageNumbers() as pageNum}
                    <button 
                        on:click={() => goToPage(pageNum)}
                        class="px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200
                               {pageNum === pagination.current_page
                                 ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                                 : 'bg-slate-700/60 hover:bg-slate-600 text-slate-300 hover:text-white'}"
                    >
                        {pageNum}
                    </button>
                {/each}
                
                {#if pagination.current_page < pagination.total_pages - 2}
                    {#if pagination.current_page < pagination.total_pages - 3}
                        <span class="text-slate-400">...</span>
                    {/if}
                    <button 
                        on:click={() => goToPage(pagination.total_pages)}
                        class="px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 
                               bg-slate-700/60 hover:bg-slate-600 text-slate-300 hover:text-white"
                    >
                        {pagination.total_pages}
                    </button>
                {/if}
            </div>
            
            <!-- Next Button -->
            <button 
                on:click={nextPage}
                disabled={!pagination.has_next}
                class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 
                       {pagination.has_next 
                         ? 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg hover:shadow-blue-600/20' 
                         : 'bg-slate-700 text-slate-400 cursor-not-allowed'}"
            >
                Next
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>
        </div>
        
        <!-- Mobile-friendly pagination info -->
        <div class="mt-4 text-center sm:hidden">
            <div class="text-sm text-slate-400">
                Page {pagination.current_page} of {pagination.total_pages}
            </div>
        </div>
    {/if}
</div>