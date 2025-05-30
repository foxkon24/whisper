#!/usr/bin/env python3
"""
Unicode Safe Whisper Transcriber
日本語ファイル名に対応した音声文字起こしツール
"""

import sys
import whisper
import os
import shutil
import tempfile
import argparse
from pathlib import Path
import time
import uuid

def safe_transcribe(model, audio_path, language='ja'):
    """
    日本語ファイル名を安全に処理するための文字起こし関数
    """
    audio_path = Path(audio_path)
    
    # 一時ディレクトリに英語名でコピー
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_audio = Path(temp_dir) / f"temp_audio_{uuid.uuid4().hex[:8]}{audio_path.suffix}"
        
        print(f"一時ファイルにコピー: {temp_audio.name}")
        shutil.copy2(audio_path, temp_audio)
        
        # Whisperで処理
        result = model.transcribe(str(temp_audio), language=language)
        
    return result

def main():
    parser = argparse.ArgumentParser(description='Unicode対応Whisper文字起こし')
    parser.add_argument('input_dir', nargs='?', default='input', help='音声ファイルの入力フォルダ')
    parser.add_argument('output_dir', nargs='?', default='output', help='テキストファイルの出力フォルダ')
    parser.add_argument('--model', default='medium', help='Whisperモデル')
    parser.add_argument('--language', default='ja', help='言語コード')
    
    args = parser.parse_args()
    
    print(f"Whisperモデル '{args.model}' をロード中...")
    model = whisper.load_model(args.model)
    
    # 音声ファイル検索
    input_path = Path(args.input_dir)
    extensions = ['*.mp3', '*.m4a', '*.wav', '*.flac', '*.ogg', '*.mp4']
    audio_files = []
    for ext in extensions:
        audio_files.extend([str(p) for p in input_path.glob(ext)])    
    if not audio_files:
        print(f"エラー: {args.input_dir} に音声ファイルが見つかりません")
        return
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n見つかったファイル:")
    for af in audio_files:
        print(f"  - {Path(af).name}")
    
    print(f"\n{len(audio_files)}個のファイルを処理開始...")
    
    for i, audio_file in enumerate(audio_files, 1):
        audio_path = Path(audio_file)
        print(f"\n[{i}/{len(audio_files)}] {audio_path.name}")
        
        start_time = time.time()
        
        try:
            # ファイル存在確認
            if not audio_path.exists():
                print(f"エラー: ファイルが存在しません")
                continue
                
            file_size = audio_path.stat().st_size
            print(f"ファイルサイズ: {file_size:,} bytes")
            
            if file_size == 0:
                print(f"エラー: ファイルサイズが0です")
                continue
            
            # Unicode安全な文字起こし実行
            print("文字起こし実行中...")
            result = safe_transcribe(model, audio_path, args.language)
            
            # 出力ファイル
            output_path = Path(args.output_dir) / f"{audio_path.stem}.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            
            elapsed = time.time() - start_time
            print(f"完了 ({elapsed:.1f}秒): {output_path.name}")
            
        except Exception as e:
            print(f"エラー: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n全ての処理が完了しました！")

if __name__ == "__main__":
    main()