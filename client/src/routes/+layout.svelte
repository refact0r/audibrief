<script>
	import '../app.css';
</script>

<div class="banner">
	Note: Due to API costs, this site has been disconnected from a live server. The data shown below
	is an example generated on 2/19/2024.
</div>
<div class="app">
	<div class="header">
		<h1>Audibrief</h1>
		<div class="links">
			<a href="/">Home</a>
			<a href="/custom">Custom</a>
			<a href="/about">About</a>
			<a href="/settings">Settings</a>
		</div>
	</div>
	<div class="main">
		<slot />
	</div>
</div>

<style>
	h1 {
		font-size: 3.5rem;
		margin: 0 1rem 0 0;
	}

	a {
		text-decoration: none;
		color: var(--text-1);
		font-size: 1.2rem;
		font-weight: 500;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.links {
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	.app {
		max-width: 60rem;
		margin: 2rem auto;
	}

	.banner {
		background-color: var(--bg-1);
		padding: 1rem;
		text-align: center;
	}
</style>
