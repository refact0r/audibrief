<script>
	import { onMount } from 'svelte';

	export let data;

	console.log(data);

	let briefs = data.articles.articles;
	let playing = false;
	let current = 0;

	function playAll() {
		if (playing) {
			stopAll();
			return;
		}

		playing = true;

		briefs.forEach((brief) => {
			brief.audioElem.addEventListener('ended', playNext);
		});

		playNext();
	}

	function playNext() {
		if (current < briefs.length) {
			briefs[current].audioElem.play();
			current += 1;
		}
	}

	function stopAll() {
		playing = false;
		current = 0;

		briefs.forEach((brief) => {
			brief.audioElem.pause();
			brief.audioElem.currentTime = 0;
			brief.audioElem.removeEventListener('ended', playNext);
		});
	}

	onMount(() => {
		// briefs.forEach((brief) => {
		// 	brief.audioElem = new Audio('data:audio/mpeg;base64,' + brief.audio);
		// });
	});
</script>

<main>
	<h1>Audibrief</h1>
	<br />

	<button on:click={playAll}>{playing ? 'Stop' : 'Play All'}</button>
	<div class="briefs">
		{#each briefs as brief, i}
			<div class="brief">
				<h2>{brief.title}</h2>

				<p style={brief.style1}>{brief.summary}</p>
				<audio
					src="data:audio/mpeg;base64,{brief.audio}"
					bind:this={briefs[i].audioElem}
					controls
					style={brief.style2}
				/>
			</div>
		{/each}
	</div>
</main>

<style>
	h1 {
		font-size: 4rem;
		margin: 0;
	}

	.brief {
		padding: 1.5rem 1.5rem 0.5rem 1.5rem;
		background: var(--bg-1);
	}

	.briefs {
		margin: 2rem 0;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	h2 {
		margin: 0 0 1rem 0;
	}

	p {
		margin: 0 0 1rem 0;
	}

	audio {
		width: calc(100% + 0.7rem);
		margin-left: -0.7rem;
	}

	audio::-webkit-media-controls {
	}

	/* remove volume control */
	audio::-webkit-media-controls-enclosure {
		background: none;
	}

	audio::-webkit-media-controls-panel {
		background: none;
		padding: 0;
	}

	audio::-webkit-media-controls-mute-button {
		display: none;
	}

	audio::-webkit-media-controls-overlay-enclosure {
		display: none;
	}

	audio::-webkit-media-controls-current-time-display,
	audio::-webkit-media-controls-time-remaining-display {
		color: var(--text-1);
		font-family: 'Satoshi', sans-serif;
		font-weight: bold;
	}
</style>
