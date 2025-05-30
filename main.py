#!/usr/bin/env python3
"""
Whisper Batch Transcriber
使用法: python whisper_batch.py input_folder output_folder
"""

import sys
import whisper
import os
import glob
import argparse
from pathlib import Path
import time
from tqdm import tqdm
import logging
from datetime import datetime

def setup_logger():
    # ログファイル名をyyyyMMddHHmm形式で生成
    log_filename = datetime.now().strftime('%Y%m%d%H%M') + '.log'
    
    # ロガーの設定
    logger = logging.getLogger('whisper_batch')
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラ（上書きモード）
    file_handler = logging.FileHandler(log_filename, mode='w')
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッタの作成
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    # ロガーのセットアップ
    logger = setup_logger()
    
    parser = argparse.ArgumentParser(description='Whisperで音声ファイルをバッチ文字起こし')
    parser.add_argument('input_dir', nargs='?', default='input', help='音声ファイルの入力フォルダ（デフォルト: input）')
    parser.add_argument('output_dir', nargs='?', default='output', help='テキストファイルの出力フォルダ（デフォルト: output）')
    parser.add_argument('--model', default='medium', help='Whisperモデル (tiny/base/small/medium/large)')
    parser.add_argument('--language', default='ja', help='言語コード (ja/en等)')
    
    args = parser.parse_args()
    
    logger.info(f"Whisperモデル '{args.model}' をロード中...")
    model = whisper.load_model(args.model)
    
    # 音声ファイル検索（Pathオブジェクトを使用してUnicode対応）
    input_path = Path(args.input_dir)
    extensions = ['*.mp3', '*.m4a', '*.wav', '*.flac', '*.ogg', '*.mp4']
    audio_files = []
    for ext in extensions:
        audio_files.extend([str(p) for p in input_path.glob(ext)])
    
    if not audio_files:
        logger.error(f"エラー: {args.input_dir} に音声ファイルが見つかりません")
        return
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    logger.info(f"見つかったファイル:")
    for af in audio_files:
        logger.info(f"  - {af}")
    
    logger.info(f"{len(audio_files)}個のファイルを処理開始...")
    
    # tqdmで進捗バーを表示
    for i, audio_file in enumerate(tqdm(audio_files, desc="ファイル進捗", unit="file"), 1):
        filename = os.path.basename(audio_file)
        logger.info(f"[{i}/{len(audio_files)}] {filename}")
        
        start_time = time.time()
        
        try:
            # ファイルパスをPathオブジェクトで処理
            audio_path = Path(audio_file)
            logger.info(f"処理中のファイルパス: {audio_path.absolute()}")
            
            # ファイル存在確認
            if not audio_path.exists():
                logger.error(f"エラー: ファイルが存在しません: {audio_path}")
                continue
                
            # ファイルサイズ確認
            file_size = audio_path.stat().st_size
            logger.info(f"ファイルサイズ: {file_size} bytes")
            
            if file_size == 0:
                logger.error(f"エラー: ファイルサイズが0です")
                continue
            
            # Whisperでの文字起こし実行
            logger.info("文字起こし実行中...")
            result = model.transcribe(str(audio_path.resolve()), language=args.language, verbose=True)
            
            # 出力ファイル
            output_path = Path(args.output_dir) / f"{audio_path.stem}.txt"
            output_file = str(output_path)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            
            elapsed = time.time() - start_time
            logger.info(f"完了 ({elapsed/60:.1f}分): {output_file}")
            
        except Exception as e:
            logger.error(f"エラー: {str(e)}")
    
    logger.info("全ての処理が完了しました！")

if __name__ == "__main__":
    main()
