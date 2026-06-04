type Props = {
  audioUrl: string;
};

export default function AudioResult({ audioUrl }: Props) {
  if (!audioUrl) return null;

  return (
    <div className="audio-result">
      <div className="audio-result__wrapper">
        <div className="audio-result__label">
          🔊 Generated Audio
        </div>
        <audio key={audioUrl} controls autoPlay>
          <source src={audioUrl} type="audio/wav" />
          Your browser does not support the audio element.
        </audio>
        <div className="audio-result__actions">
          <a href={audioUrl} download className="btn btn--outline">
            ⬇ Download WAV
          </a>
        </div>
      </div>
    </div>
  );
}