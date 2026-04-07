# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gradio as gr
from pathlib import Path
from typing import List, Tuple, Optional
from utils import VideoSearchAgent

agent = VideoSearchAgent()
MAX_PREVIEWS = 10

APP_CSS = """
:root {
    --nv-green: #76B900;
    --nv-green-dark: #5f9400;
    --panel-bg: #FFFFFF;
    --panel-border: #DCE3EA;
    --text-primary: #111827;
    --text-secondary: #4B5563;
}

body, .gradio-container {
    background: linear-gradient(180deg, #F7FAFC 0%, #EEF3F8 100%);
    color: var(--text-primary);
}

.gradio-container {
    --color-accent: #76B900 !important;
    --color-accent-soft: rgba(118, 185, 0, 0.16) !important;
    --color-accent-soft-dark: rgba(118, 185, 0, 0.24) !important;
    --button-primary-background-fill: #76B900 !important;
    --button-primary-background-fill-hover: #5f9400 !important;
    --button-primary-border-color: #76B900 !important;
    --button-primary-border-color-hover: #5f9400 !important;
    --slider-color: #76B900 !important;
}

.app-shell {
    max-width: 1320px;
    margin: 0 auto;
    padding: 8px 8px 16px 8px;
}

.hero {
    border: 1px solid var(--panel-border);
    border-top: 4px solid var(--nv-green);
    background: linear-gradient(120deg, rgba(118,185,0,0.12) 0%, #FFFFFF 52%, #F7FAFC 100%);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
}

.hero-row {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
    flex-wrap: wrap;
}

.hero h1 {
    margin: 0 0 6px 0;
    font-size: 2rem;
    letter-spacing: 0.2px;
    color: #111827;
    line-height: 1.15;
}

.hero p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.98rem;
    max-width: 760px;
}

.panel {
    border: 1px solid var(--panel-border);
    background: var(--panel-bg);
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.panel-title {
    margin: 0 0 10px 0;
    font-size: 1.02rem;
    font-weight: 700;
    color: #111827;
    border-left: 4px solid var(--nv-green);
    padding-left: 10px;
}

.gr-button,
.gr-button-primary,
button.gr-button {
    background: var(--nv-green) !important;
    border: 1px solid var(--nv-green) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    transition: background-color 0.2s ease, border-color 0.2s ease !important;
}

.gr-button:hover,
.gr-button-primary:hover,
button.gr-button:hover {
    background: var(--nv-green-dark) !important;
    border-color: var(--nv-green-dark) !important;
}

button.primary,
button.secondary {
    background: var(--nv-green) !important;
    border-color: var(--nv-green) !important;
    color: #FFFFFF !important;
}

button.primary:hover,
button.secondary:hover {
    background: var(--nv-green-dark) !important;
    border-color: var(--nv-green-dark) !important;
}

input[type="range"] {
    accent-color: var(--nv-green) !important;
}

input[type="range"]::-webkit-slider-thumb {
    background: var(--nv-green) !important;
}

input[type="range"]::-moz-range-thumb {
    background: var(--nv-green) !important;
}

#results-box {
    border: 1px solid #E5EAF0;
    border-radius: 10px;
    background: #FAFCFE;
    padding: 10px;
    min-height: 510px;
}

#preview-stack {
    min-height: 520px;
    max-height: 620px;
    overflow-y: auto;
    padding-right: 4px;
}

.preview-card {
    border: 1px solid #E5EAF0;
    border-radius: 10px;
    background: #FAFCFE;
    padding: 8px;
    margin-bottom: 10px;
}
"""


def _safe_video_path(path_value: Optional[str]) -> Optional[str]:
    if not path_value:
        return None
    path_obj = Path(path_value)
    return str(path_obj) if path_obj.is_file() else None


def search_videos(text_query: str, file_path: str, top_k: int) -> Tuple[str, List[Tuple[str, str]]]:
    try:
        if file_path and file_path.strip():
            query = file_path.strip()
        elif text_query and text_query.strip():
            query = text_query.strip()
        else:
            return "Please provide either a text query or a file path.", []
        
        matches = agent.search(query, top_k=top_k)
        
        if not matches:
            return "No matches found.", []
        
        results_text = f"### Found {len(matches)} matches:\n\n"
        previews: List[Tuple[str, str]] = []
        for i, match in enumerate(matches, 1):
            results_text += f"**{i}. {match['video_name']}**\n"
            results_text += f"   - Similarity Score: {match['score']:.4f}\n"
            
            if 'text_description' in match and match['text_description']:
                results_text += f"   - Description: *{match['text_description']}*\n"
            
            results_text += f"   - Path: `{match['video_path']}`\n\n"

            safe_path = _safe_video_path(match["video_path"])
            if safe_path:
                caption = f"{i}. {match['video_name']} | Score: {match['score']:.4f}"
                previews.append((safe_path, caption))

        return results_text, previews
        
    except Exception as e:
        return f"Error: {str(e)}", []

def create_interface():
    with gr.Blocks(title="NVIDIA Video Search", css=APP_CSS) as demo:
        with gr.Column(elem_classes=["app-shell"]):
            gr.Markdown(
                """
                <div class="hero">
                  <div class="hero-row">
                    <div>
                      <h1>Multimodal Video Search</h1>
                      <p>Search your dataset with text, image, or video prompts and quickly preview the most similar matches.</p>
                    </div>
                  </div>
                </div>
                """
            )

            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    with gr.Column(elem_classes=["panel"]):
                        gr.Markdown('<div class="panel-title">Query Input</div>')

                        text_input = gr.Textbox(
                            label="Text Query",
                            lines=3,
                            placeholder="Example: robot picks up avocado from shelf",
                        )

                        file_path_input = gr.Textbox(
                            label="File Path (Image or Video)",
                            lines=1,
                            placeholder="/absolute/path/to/query.jpg or .mp4",
                        )

                        top_k_slider = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1,
                            label="Top Results",
                        )

                        search_btn = gr.Button("Search", variant="primary", size="lg")

                with gr.Column(scale=1):
                    with gr.Column(elem_classes=["panel"]):
                        gr.Markdown('<div class="panel-title">Search Results</div>')

                        results_output = gr.Markdown(
                            value="Run a search to see ranked matches and similarity scores.",
                            elem_id="results-box",
                        )

                with gr.Column(scale=1):
                    with gr.Column(elem_classes=["panel"]):
                        gr.Markdown('<div class="panel-title">Top K Matches</div>')
                        with gr.Column(elem_id="preview-stack"):
                            preview_labels: List[gr.Markdown] = []
                            preview_videos: List[gr.Video] = []
                            for _ in range(MAX_PREVIEWS):
                                with gr.Column(elem_classes=["preview-card"]):
                                    preview_labels.append(gr.Markdown(value="", visible=False))
                                    preview_videos.append(
                                        gr.Video(
                                            value=None,
                                            show_label=False,
                                            autoplay=False,
                                            height=210,
                                            visible=False,
                                        )
                                    )
        
        def search_and_update(*args):
            results_text, previews = search_videos(*args)
            label_updates = []
            video_updates = []

            for i in range(MAX_PREVIEWS):
                if i < len(previews):
                    path, caption = previews[i]
                    label_updates.append(gr.update(value=f"**{caption}**", visible=True))
                    video_updates.append(gr.update(value=path, visible=True))
                else:
                    label_updates.append(gr.update(value="", visible=False))
                    video_updates.append(gr.update(value=None, visible=False))

            return [results_text] + label_updates + video_updates
        
        search_btn.click(
            fn=search_and_update,
            inputs=[text_input, file_path_input, top_k_slider],
            outputs=[results_output] + preview_labels + preview_videos
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
