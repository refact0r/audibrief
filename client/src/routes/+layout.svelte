<script>
	import '../app.css';
</script>

<div class="app">
	<div class="header">
		<h1>Audibrief</h1>
		<div class="links">
			<a href="/">Home</a>
			<a href="/about">Custom</a>
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
		margin: 3rem auto;
	}
</style>
