//! Sonda: quais curtidas somem entre a colecao e o metadado.
//!
//! A colecao devolve os ids; o metadado em lote devolve as faixas. Faixa que o
//! segundo passo nao devolve some da tela sem aviso. Esta sonda lista essas.
//!
//! ```text
//! cargo run -p morune-desktop --example sonda-curtidas [busca]
//! ```
//!
//! Usa a sessao guardada no cofre do Windows. Nao toca audio nem escreve nada
//! na conta.

use std::collections::HashSet;
use std::sync::Arc;

use morune_core::catalog::SearchKind;
use morune_spotify::SpotifyBackend;

#[allow(dead_code)]
#[path = "../src/ordem_curtidas.rs"]
mod ordem_curtidas;

fn main() {
    let credenciais = morune_storage::platform_store();
    let cache_audio = std::env::temp_dir().join("morune-sonda-curtidas");
    let backend = SpotifyBackend::new(
        Arc::from(credenciais),
        morune_core::playback::AudioSettings::default(),
        &cache_audio,
    )
    .expect("backend do Spotify");

    let perfil = backend
        .block_on(backend.authenticator().restore())
        .expect("restaurar a sessao guardada");
    if perfil.is_none() {
        eprintln!("Nao ha sessao guardada no cofre do Windows.");
        std::process::exit(1);
    }

    let library = backend.library();
    let ids = backend
        .block_on(library.saved_track_ids())
        .expect("ids da colecao");
    println!("colecao: {} ids", ids.len());
    for id in ids.iter().take(5) {
        println!("  primeiro: {}", id.id);
    }

    let faixas = backend
        .block_on(library.tracks_by_ids(&ids))
        .expect("metadado");
    println!("metadado: {} faixas", faixas.len());

    let vieram: HashSet<&str> = faixas.iter().map(|t| &*t.id.id).collect();
    for (i, id) in ids.iter().enumerate() {
        if !vieram.contains(&*id.id) {
            println!("  SUMIU posicao {i}: spotify:track:{}", id.id);
        }
    }
    for t in faixas.iter().take(3) {
        println!("  topo: {:?}", t);
    }

    let datas = backend
        .block_on(library.saved_track_dates())
        .expect("datas da colecao");
    for (id, quando) in datas.iter().take(5) {
        println!("  data: {} {}", id.id, quando);
    }

    // A ordem gravada pelo app instalado (so leitura), aplicada as datas reais.
    if let Ok(pasta) = std::env::var("PASTA_ORDEM") {
        let ordem = ordem_curtidas::ler(std::path::Path::new(&pasta));
        let lista = ordem.aplicar(&datas);
        let alvo = lista.iter().position(|id| &*id.id == "1WMYcKZ85zdl8RCqhin7xM");
        println!("ordem aplicada: {} faixas; Temporal de Amor na posicao {:?}", lista.len(), alvo.map(|i| i + 1));
        let topo: Vec<_> = lista.iter().take(5).cloned().collect();
        let nomes = backend.block_on(library.tracks_by_ids(&topo)).expect("topo");
        for t in nomes {
            println!("  ordem topo: {}", t.name);
        }
    }

    if let Some(busca) = std::env::args().nth(1) {
        match backend.block_on(backend.catalog().search(&busca, SearchKind::Tracks, 10)) {
            Ok(r) => {
                println!("busca {busca:?}: {} faixas", r.tracks.len());
                for t in &r.tracks {
                    println!("  {} ({})", t.name, t.id.id);
                }
            }
            Err(e) => println!("busca FALHOU: {e}"),
        }
    }
}
