<script>
	import { onMount } from 'svelte';

	export let data;

	console.log(data);

	let briefs = data.articles.articles;

	function playAll() {
		let i = 0;

		function playNext() {
			if (i < briefs.length) {
				console.log(briefs[i].audioElem);
				briefs[i].audioElem.play();
				i += 1;
			}
		}

		briefs.forEach((brief) => {
			brief.audioElem.addEventListener('ended', playNext);
		});

		playNext();
	}

	onMount(() => {
		briefs.forEach((brief) => {
			brief.audioElem = new Audio('data:audio/mpeg;base64,' + brief.audio);
		});
	});
</script>

<h1>Audibrief</h1>
<br />

<button on:click={playAll}>Play All</button>

{#each briefs as brief, i}
	<div>
		<h2>{brief.title}</h2>
		<p>{brief.summary}</p>
	</div>
{/each}

<style>
	h1 {
		font-size: 4rem;
		margin: 0;
	}

	audio {
		width: 100%;
		background: none;
	}
</style>
