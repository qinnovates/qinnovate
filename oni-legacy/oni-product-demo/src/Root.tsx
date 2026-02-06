import { Composition } from "remotion";
import { ONIDemoVideo } from "./ONIDemoVideo";
import { videoConfig } from "./data/oni-theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ONIDemoVideo"
        component={ONIDemoVideo}
        durationInFrames={videoConfig.durationInFrames}
        fps={videoConfig.fps}
        width={videoConfig.width}
        height={videoConfig.height}
      />
    </>
  );
};
