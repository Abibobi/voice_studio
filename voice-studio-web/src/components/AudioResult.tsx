type Props = {
    audioUrl: string;
};

export default function AudioResult({ audioUrl }: Props) {
    if (!audioUrl) return null;

    return (
        <div style={{ marginTop: 16 }}>
            {/* key forces React to create a brand-new <audio> element for each URL */}
            <audio key={audioUrl} controls autoPlay style={{ width: "100%" }}>
                <source src={audioUrl} type="audio/wav" />
                Your browser does not support the audio element.
            </audio>
            <div style={{ marginTop: 10 }}>
                <a href={audioUrl} download className="btn">
                    Download Audio
                </a>
            </div>
        </div>
    );
}