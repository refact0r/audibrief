<script>
	export let data;

	console.log(data);

	let briefs = data.articles.articles;
	let playing = false;
	let current = 0;

	// initialize and start playing audio in sequence
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

	// play the next audio
	function playNext() {
		if (current < briefs.length) {
			briefs[current].audioElem.play();
			current += 1;
			briefs[current].style1 = 'height: auto;';
		}
	}

	// stop all audio
	function stopAll() {
		playing = false;
		current = 0;

		briefs.forEach((brief) => {
			brief.audioElem.pause();
			brief.audioElem.currentTime = 0;
			brief.audioElem.removeEventListener('ended', playNext);
		});
	}
</script>

<main>
	<div class="header">
		<p>Top 5 news stories from Google News</p>
		<button on:click={playAll}>{playing ? 'Stop' : 'Play All'}</button>
	</div>
	<br />
	<div class="briefs">
		{#each briefs as brief, i}
			<div class="brief">
				<h2>{brief.title}</h2>

				<p>{brief.summary}</p>
				<audio
					src="data:audio/mpeg;base64,{brief.audio}"
					bind:this={briefs[i].audioElem}
					controls
				/>
			</div>
		{/each}
	</div>
</main>

<style>
	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin: 1rem 0 0 0;
	}

	.brief {
		padding: 1.5rem;
		background: var(--bg-1);
		display: flex;
		flex-direction: column;
		border-radius: 2rem;
	}

	.briefs {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	p {
		font-size: 1.2rem;
	}

	h2 {
		margin: 0;
	}

	.briefs p {
		margin: 1rem 0;
	}

	audio {
		width: calc(100% + 0.6rem);
		margin-left: -0.6rem;
		height: 2rem;
	}

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
